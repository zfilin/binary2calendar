# Binary2Calendar

Binary2Calendar is a Home Assistant custom integration that converts state changes from binary sensors and input_boolean entities into calendar events.

The integration monitors binary entities and creates calendar entries when the entity state matches a configured trigger state. This allows tracking device activity over time through the standard Home Assistant calendar interface.

---

## Features

- Converts binary sensor state changes into calendar events
- Supports binary_sensor and input_boolean entities
- Configurable trigger state (on or off)
- Configurable polling interval
- Configurable history retention period
- English and Ukrainian translations

---

## Installation

### Via HACS (recommended)

1. Open HACS in Home Assistant.
2. Go to Integrations.
3. Click the three dots menu and select "Add Repository".
4. Enter the repository URL: `https://github.com/zfilin/binary2calendar`.
5. Click Add.
6. Restart Home Assistant.
7. Go to Settings → Devices & Services → Add Integration.
8. Search for Binary2Calendar and add it.

### Manual installation

1. Copy the `custom_components/binary2calendar` directory into your Home Assistant `custom_components` folder.
2. Restart Home Assistant.
3. Go to Settings → Devices & Services → Add Integration.
4. Search for Binary2Calendar and add it.

---

## Configuration

Configuration is done through the Home Assistant UI config flow. Add a new integration and select the binary sensor or input_boolean entity you want to track.

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| entity_id | string | — | Binary sensor or input_boolean entity ID |
| title | string | — | Calendar title shown in the UI |
| trigger_state | string | on | State that starts an event (on or off) |
| update_interval | integer | 5 | Polling interval in minutes (1–1440) |
| history_days | integer | 30 | Days of history to retain (1–365) |

---

## How It Works

Binary2Calendar polls the specified binary entity at the configured interval. When the entity state changes to the trigger state, a calendar event starts. When the state changes back, the event ends. Events are retrieved from the Home Assistant recorder history.

---

## Requirements

- Home Assistant Core ≥ 0.60.0
- Python 3.10+
- Dependencies: python-dateutil, voluptuous

---

## Support

- Documentation: [GitHub Wiki](https://github.com/zfilin/binary2calendar)
- Issues: [Issue Tracker](https://github.com/zfilin/binary2calendar/issues)

## License

This project is licensed under the [MIT License](LICENSE).

Copyright (c) 2026 Green Owl