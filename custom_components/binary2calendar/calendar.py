import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entities import Binary2CalendarCalendar
from .updater import CalendarUpdater

_LOGGER = logging.getLogger(__name__)


def _entry_config(entry: ConfigEntry) -> dict:
    """Return the effective config: entry.data overridden by entry.options."""
    return {**entry.data, **entry.options}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one binary2calendar calendar for this config entry."""
    cfg = _entry_config(config_entry)
    if not cfg.get("entity_id"):
        _LOGGER.error("binary2calendar: missing entity_id in entry data")
        return

    entity = Binary2CalendarCalendar(
        hass,
        cfg,
        unique_id=f"{DOMAIN}.{cfg['entity_id']}",
    )

    async_add_entities([entity], True)  # update_before_add=True

    # Start the updater (poller) for this calendar.
    updater = CalendarUpdater(hass, [cfg])
    updater.entity = entity  # poller must update the registered entity
    await updater.async_start()

    # Store entity and updater so we can stop them on unload.
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {
        "entity": entity,
        "updater": updater,
    }