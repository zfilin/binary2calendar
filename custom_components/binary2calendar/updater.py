import logging
import asyncio
from datetime import timedelta
from datetime import datetime
from homeassistant.util import dt as dt_util

from .history import async_get_binary_history
from .entities import Binary2CalendarCalendar
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class CalendarUpdater:
    """Poller that periodically updates events for all calendars."""

    def __init__(self, hass, calendar_configs):
        """calendar_configs: list[dict] – each dict contains calendar settings."""
        self.hass = hass
        self.calendar_configs = calendar_configs
        self._tasks: list[asyncio.Task] = []
        self.entity = None  # registered HA calendar entity

    async def async_start(self):
        """Start the poller for all calendars."""
        for cfg in self.calendar_configs:
            task = self._create_task(cfg)
            self._tasks.append(task)

    def _create_task(self, cfg) -> asyncio.Task:
        """Create a task that calls `_update_calendar` at the given interval."""

        async def _updater():
            while True:
                try:
                    await self._update_calendar(cfg)
                except Exception as exc:
                    _LOGGER.error(f"binary2calendar: error updating calendar {cfg.get('title')}: {exc}")
                # Wait for the specified interval (in minutes)
                interval = timedelta(minutes=cfg.get("update_interval", 5))
                await asyncio.sleep(interval.total_seconds())

        return asyncio.create_task(_updater())

    async def _update_calendar(self, cfg):
        """
        Read history for the last `history_days` and update calendar events.
        """
        title = cfg.get("title", "Unknown")
        entity_id = cfg.get("entity_id")
        history_days = cfg.get("history_days", 30)

        if not entity_id:
            _LOGGER.error(f"binary2calendar: missing entity_id for calendar {title}")
            return

        try:
            records = await async_get_binary_history(
                self.hass,
                entity_id,
                history_days,
            )
        except Exception as exc:
            _LOGGER.error(
                f"binary2calendar: failed to get history for {entity_id}: {exc}",
                exc_info=True,
            )
            return

        if not records:
            _LOGGER.warning(
                f"binary2calendar: no history for {entity_id} over the last {history_days} days"
            )
            return

        # Update the exact entity registered in Home Assistant.
        # Creating a new calendar object would not push events to the UI.
        entity = getattr(self, "entity", None)
        if entity is None:
            # Fallback: search hass.data by entity_id.
            for entry_data in self.hass.data.get(DOMAIN, {}).values():
                if isinstance(entry_data, dict):
                    entity = entry_data.get("entity")
                    if entity is not None and getattr(entity, "unique_id", None) == f"{DOMAIN}.{entity_id}":
                        break
                elif isinstance(entry_data, Binary2CalendarCalendar):
                    if getattr(entry_data, "unique_id", None) == f"{DOMAIN}.{entity_id}":
                        entity = entry_data
                        break
        if entity is None:
            _LOGGER.error(f"binary2calendar: calendar entity {entity_id} not found")
            return

        entity.update_events(records)

        _LOGGER.debug(f"binary2calendar: calendar {title} updated ({len(records)} records)")

    async def stop_all(self):
        """Cancel all poller tasks."""
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
