DOMAIN = "binary2calendar"

CONF_ENTITY_ID = "entity_id"
CONF_TITLE = "title"
CONF_START = "start"
CONF_END = "end"
CONF_TRIGGER_STATE = "trigger_state"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_HISTORY_DAYS = "history_days"
CONF_ICON = "icon"

DEFAULT_HISTORY_DAYS = 30
DEFAULT_UPDATE_INTERVAL = 5  # minutes
DEFAULT_TRIGGER_STATE = "on"


class CalendarConfig:
    """Dataclass-ish holder for calendar settings."""

    def __init__(
        self,
        entity_id: str,
        title: str = "",
        start: str = "",
        end: str = "",
        trigger_state: str = DEFAULT_TRIGGER_STATE,
        update_interval: float = DEFAULT_UPDATE_INTERVAL,
        history_days: int = DEFAULT_HISTORY_DAYS,
    ) -> None:
        self.entity_id = entity_id
        self.title = title
        self.start = start
        self.end = end
        self.trigger_state = trigger_state
        self.update_interval = update_interval
        self.history_days = history_days

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "title": self.title,
            "start": self.start,
            "end": self.end,
            "trigger_state": self.trigger_state,
            "update_interval": self.update_interval,
            "history_days": self.history_days,
        }
