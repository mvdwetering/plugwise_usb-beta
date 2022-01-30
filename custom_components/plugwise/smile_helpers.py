"""Plugwise Smile Helper Classes."""
from .const import (
    COOLING_ICON,
    FLAME_ICON,
    FLOW_OFF_ICON,
    FLOW_ON_ICON,
    HEATING_ICON,
    IDLE_ICON,
    NO_NOTIFICATION_ICON,
    NOTIFICATION_ICON,
    SEVERITIES,
)


def icon_selector(arg, state):
    """Icon-selection helper function."""
    selector = {
        # Device State icons
        "cooling": COOLING_ICON,
        "dhw-heating": FLAME_ICON,
        "dhw and cooling": COOLING_ICON,
        "dhw and heating": HEATING_ICON,
        "heating": HEATING_ICON,
        "idle": IDLE_ICON,
        # Binary Sensor icons
        "dhw_state": FLOW_ON_ICON if state else FLOW_OFF_ICON,
        "flame_state": FLAME_ICON if state else IDLE_ICON,
        "slave_boiler_state": FLAME_ICON if state else IDLE_ICON,
        "plugwise_notification": NOTIFICATION_ICON if state else NO_NOTIFICATION_ICON,
    }
    return selector.get(arg)


def get_preset_temp(preset, cooling_active, data):
    """Obtain the matching preset setpoint temperature ."""
    if cooling_active:
        return data["presets"].get(preset)[1]
    return data["presets"].get(preset)[0]


class GWBinarySensor:
    """Represent the Plugwise Smile/Stretch binary_sensor."""

    def __init__(self, data):
        """Initialize the Gateway."""
        self._attributes = {}
        self._data = data
        self._notification = {}

    @property
    def extra_state_attributes(self):
        """Gateway binary_sensor extra state attributes."""
        notify = self._data[0].get("notifications")
        self._notification = {}
        for severity in SEVERITIES:
            self._attributes[f"{severity.upper()}_msg"] = []

        if notify:
            for notify_id, details in notify.items():
                for msg_type, msg in details.items():
                    if msg_type not in SEVERITIES:
                        msg_type = "other"  # pragma: no cover
                    self._attributes[f"{msg_type.upper()}_msg"].append(msg)
                    self._notification[notify_id] = f"{msg_type.title()}: {msg}"
            return self._attributes

        return None

    @property
    def notification(self):
        """Plugwise Notification message."""
        return self._notification


class GWThermostat:
    """Represent a Plugwise Thermostat Device."""

    def __init__(self, data, dev_id):
        """Initialize the Thermostat."""

        self._data = data
        self._dev_id = dev_id
        self._gateway_id = self._data[0].get("gateway_id")
        self._heater_id = self._data[0].get("heater_id")

    @property
    def cooling_active(self):
        """Cooling state."""
        if self._heater_id is not None:
            return self._data[1][self._heater_id].get("cooling_active")

        return None

    @property
    def cooling_state(self):
        """Cooling state."""
        cooling_state = None
        if self._data[0]["active_device"]:
            cooling_state = self._data[1][self._heater_id].get("cooling_state")
            # When control_state is present, prefer this data
            if "control_state" in self._data[1][self._dev_id]:
                cooling_state = (
                    self._data[1][self._dev_id]["control_state"] == "cooling"
                )

        return cooling_state

    @property
    def heating_state(self):
        """Heating state."""
        heating_state = None
        if self._data[0]["active_device"]:
            heating_state = self._data[1][self._heater_id].get("heating_state")
            # When control_state is present, prefer this data
            if "control_state" in self._data[1][self._dev_id]:
                heating_state = (
                    self._data[1][self._dev_id]["control_state"] == "heating"
                )

        return heating_state