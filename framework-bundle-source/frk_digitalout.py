from digitalio import DigitalInOut, DriveMode

class DigitalOut:
    drive_mode = "PUSH_PULL"
    initial_value = False
    value = False
    invert = False
    enable = True
    
    _drive_modes = {"NONE": None,
                    "PUSH_PULL": DriveMode.PUSH_PULL,
                    "OPEN_DRAIN": DriveMode.OPEN_DRAIN}
    
    def _init_device(self):
        self._device = DigitalInOut(self._pin)
        self._device.switch_to_output(value=self._initial_value, drive_mode=self._drive_modes[self._drive_mode])
    
    def _set_value(self, v):
        self._device.value = self._value = (bool(v) ^ self._invert) & self._enable
