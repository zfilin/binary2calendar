"""Config flow for Binary2Calendar integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, selector

from .const import (
    DOMAIN,
    CONF_ENTITY_ID,
    CONF_TITLE,
    CONF_TRIGGER_STATE,
    CONF_UPDATE_INTERVAL,
    CONF_HISTORY_DAYS,
    DEFAULT_HISTORY_DAYS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_TRIGGER_STATE,
)

_LOGGER = logging.getLogger(__name__)


def _build_schema(defaults: dict) -> vol.Schema:
    """Build the settings schema with the given defaults."""
    return vol.Schema(
        {
            vol.Required(
                CONF_ENTITY_ID,
                default=defaults.get(CONF_ENTITY_ID, ""),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["binary_sensor", "input_boolean"]
                )
            ),
            vol.Optional(CONF_TITLE, default=defaults.get(CONF_TITLE, "")): str,
            vol.Optional(
                CONF_TRIGGER_STATE,
                default=defaults.get(CONF_TRIGGER_STATE, DEFAULT_TRIGGER_STATE),
            ): vol.In(["on", "off"]),
            vol.Optional(
                CONF_UPDATE_INTERVAL,
                default=defaults.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            vol.Optional(
                CONF_HISTORY_DAYS,
                default=defaults.get(CONF_HISTORY_DAYS, DEFAULT_HISTORY_DAYS),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=365)),
        }
    )


def _validate_entity(hass: HomeAssistant, entity_id: str) -> bool:
    """Return True if entity_id is a binary_sensor or input_boolean."""
    registry = er.async_get(hass)
    entity = registry.async_get(entity_id)
    return entity is not None and entity.domain in ("binary_sensor", "input_boolean")


class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handles the config flow for one calendar."""

    async def async_step_user(self, user_input: dict | None = None):
        """Define the user flow."""
        errors = {}
        if user_input is not None:
            entity_id = user_input.get(CONF_ENTITY_ID, "")
            if not _validate_entity(self.hass, entity_id):
                errors["base"] = "invalid_entity"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_TITLE, "Binary2Calendar"),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input or {}),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> "OptionsFlowHandler":
        """Return the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Allow editing the settings of an existing calendar."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Manage the calendar settings."""
        errors = {}
        if user_input is not None:
            entity_id = user_input.get(CONF_ENTITY_ID, "")
            if not _validate_entity(self.hass, entity_id):
                errors["base"] = "invalid_entity"
            else:
                return self.async_create_entry(title="", data=user_input)

        # Merge stored data and options so the current values are pre-filled.
        current = {**self._entry.data, **self._entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(current),
            errors=errors,
        )