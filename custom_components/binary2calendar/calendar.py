import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entities import Binary2Calendar
from .updater import CalendarUpdater

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one binary2calendar calendar for this config entry."""
    cfg = {**config_entry.data, **config_entry.options}
    if not cfg.get("entity_id"):
        _LOGGER.error("binary2calendar: missing entity_id in entry data")
        return

    entity = Binary2Calendar(
        hass,
        cfg,
        unique_id=f"{DOMAIN}.{cfg['entity_id']}",
    )

    async_add_entities([entity], True)  # update_before_add=True

    # Start the updater (poller) for this calendar.
    updater = CalendarUpdater(hass, [cfg], entity=entity)
    await updater.async_start()

    # Store entity and updater so we can stop them on unload.
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {
        "entity": entity,
        "updater": updater,
    }
