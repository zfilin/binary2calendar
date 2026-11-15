import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS = ["calendar"]

_LOGGER = logging.getLogger(__name__)


def _entry_config(entry: ConfigEntry) -> dict:
    """Return the effective config: entry.data overridden by entry.options."""
    return {**entry.data, **entry.options}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Binary2Calendar from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    # Store raw entry data (contains one calendar config).
    hass.data[DOMAIN][entry.entry_id] = _entry_config(entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload the entry whenever its options are updated.
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Stop the updater task if exists
        data = hass.data[DOMAIN].pop(entry.entry_id, None)
        if data and isinstance(data, dict) and "updater" in data:
            await data["updater"].stop_all()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)