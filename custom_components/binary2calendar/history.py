import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder import history as recorder_history

_LOGGER = logging.getLogger(__name__)


async def async_get_binary_history(hass: HomeAssistant, entity_id: str, days: int) -> list[dict]:
    """
    Return a list of history records (state changes) for the last `days` days
    for the specified binary entity.

    Uses the recorder API (Home Assistant 2022.5+).
    """
    now = dt_util.utcnow()
    start_time = now - timedelta(days=days)

    try:
        instance = get_instance(hass)

        func = getattr(recorder_history, "state_changes_during_period", None)
        if func is not None:
            # HA 2022.5+ stable API
            result = await instance.async_add_executor_job(
                func,
                hass,
                start_time,
                now,
                entity_id,
                no_attributes=False,
                descending=False,
                limit=None,
                include_start_time_state=True,
            )
        else:
            func = getattr(recorder_history, "get_significant_states", None)
            if func is None:
                _LOGGER.error("binary2calendar: no history function found in recorder")
                return []
            result = await instance.async_add_executor_job(
                func, hass, start_time, now, [entity_id]
            )

        states: list[Any] = []
        if isinstance(result, dict):
            states = result.get(entity_id, [])
        elif isinstance(result, list):
            states = [
                state
                for state in result
                if getattr(state, "entity_id", None) == entity_id
            ]

        events = []
        for state in states:
            last_changed = getattr(state, "last_changed", None)
            if isinstance(last_changed, datetime):
                time_str = last_changed.isoformat()
            else:
                time_str = str(last_changed)

            events.append(
                {
                    "entity_id": entity_id,
                    "state": getattr(state, "state", None),
                    "last_changed": time_str,
                }
            )
        return events
    except Exception:
        _LOGGER.exception("binary2calendar: error retrieving history for %s", entity_id)
        return []
