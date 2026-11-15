import logging
from datetime import datetime
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class Binary2CalendarCalendar(CalendarEntity):
    """Calendar that represents events from a binary entity's history."""

    def __init__(self, hass: HomeAssistant, config: dict, unique_id: str):
        self.hass = hass
        self._config = config
        self._unique_id = unique_id
        self._attr_name = config["title"]
        self._attr_icon = "mdi:calendar"
        self._events: list[CalendarEvent] = []

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def event(self):
        """Current event (if one is open)."""
        now = dt_util.utcnow()
        for ev in self._events:
            if ev.start <= now <= ev.end:
                return ev
        return None

    async def async_get_events(self, hass, start_date, end_date):
        """Return events between start_date and end_date."""
        return [ev for ev in self._events if ev.start < end_date and ev.end > start_date]

    async def async_add_event(self, hass, event):
        """Add a new event to the calendar."""
        # Events are already built in _build_events, so just store them.
        self._events.append(event)

    async def async_delete_event(self, hass, uid, recurrence_id=None):
        """Delete an event from the calendar."""
        self._events = [ev for ev in self._events if ev.uid != uid]

    def update_events(self, records):
        """Build events from a list of history records."""
        trigger = self._config["trigger_state"]
        prev_state = None
        events_data = []

        for rec in records:
            state = rec.get("new_state", rec.get("state"))
            if not state:
                continue
            time = rec.get("last_changed") or rec.get("last_updated")
            if not time:
                continue
            try:
                dt = dt_util.parse_datetime(time)
            except Exception:
                _LOGGER.error(f"binary2calendar: could not parse time {time}")
                continue

            # If the state turned on after being off, open an event.
            if state == trigger and prev_state != trigger:
                events_data.append({"start": dt, "end": None})
            # If the state turned off after being on, close the event.
            elif state != trigger and prev_state == trigger:
                if events_data:
                    events_data[-1]["end"] = dt
            prev_state = state

        # Close any open events with the current time
        now = dt_util.utcnow()
        for ev in events_data:
            if ev["end"] is None:
                ev["end"] = now

        # Clear old events and build new ones
        self._events = []
        for ev in events_data:
            if ev["start"] and ev["end"]:
                event = CalendarEvent(
                    start=ev["start"],
                    end=ev["end"],
                    summary=self._config["title"],
                    uid=f"{self._config['entity_id']}-{ev['start'].isoformat()}",
                )
                self._events.append(event)

    def to_dict(self):
        """Return the config as a dict."""
        return {
            "name": self._attr_name,
            "icon": self._attr_icon,
        }