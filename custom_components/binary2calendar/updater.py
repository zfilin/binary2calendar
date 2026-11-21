import logging
import asyncio
from datetime import timedelta


from .history import async_get_binary_history
from .entities import Binary2Calendar
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class CalendarUpdater:
    """Poller that periodically updates events for all calendars."""

    def __init__(
        self, hass, calendar_configs: list[dict], entity: Binary2Calendar | None = None
    ) -> None:
        """calendar_configs: list[dict] – each dict contains calendar settings."""
        self.hass = hass
        self.calendar_configs = calendar_configs
        self._tasks: list[asyncio.Task] = []
        self.entity = entity  # registered HA calendar entity

    async def async_start(self) -> None:
        """Start the poller for all calendars."""
        for cfg in self.calendar_configs:
            task = self._create_task(cfg)
            self._tasks.append(task)

    def _create_task(self, cfg: dict) -> asyncio.Task:
        """Create a task that calls `_update_calendar` at the given interval."""

        async def _updater() -> None:
            while True:
                try:
                    await self._update_calendar(cfg)
                except Exception:
                    _LOGGER.exception(
                        "binary2calendar: error updating calendar %s",
                        cfg.get("title"),
                    )
                interval = timedelta(minutes=cfg.get("update_interval", 5))
                await asyncio.sleep(interval.total_seconds())

        return asyncio.create_task(_updater())

    async def _update_calendar(self, cfg: dict) -> None:
        """Read history for the last `history_days` and update calendar events."""
        title = cfg.get("title", "Unknown")
        entity_id = cfg.get("entity_id")
        history_days = cfg.get("history_days", 30)

        if not entity_id:
            _LOGGER.error("binary2calendar: missing entity_id for calendar %s", title)
            return

        try:
            records = await async_get_binary_history(self.hass, entity_id, history_days)
        except Exception:
            _LOGGER.exception("binary2calendar: failed to get history for %s", entity_id)
            return

        if not records:
            _LOGGER.debug(
                "binary2calendar: no history for %s over the last %s days",
                entity_id,
                history_days,
            )
            return

        entity = self.entity
        if entity is None:
            _LOGGER.error(
                "binary2calendar: calendar entity %s not found", entity_id
            )
            return

        entity.update_events(records)

        _LOGGER.debug(
            "binary2calendar: calendar %s updated (%s records)", title, len(records)
        )

    async def stop_all(self) -> None:
        """Cancel all poller tasks."""
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
