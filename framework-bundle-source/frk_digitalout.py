from framework import Driver
import digitalio

class DigitalOut(Driver):
    _defaults = {'drive_mode': 'PUSH_PULL',
                 'initial_value': False,
                 'enable': True,
                 'invert': False,
                 'value': False}

    _get_set_del = {'drive_mode': 'g',
                    'initial_value': 'g',
                    'enable': 'gs',
                    'invert': 'gs',
                    'value': 'gs'}

    _drive_modes = {'NONE': None,
                    'PUSH_PULL': digitalio.DriveMode.PUSH_PULL,
                    'OPEN_DRAIN': digitalio.DriveMode.OPEN_DRAIN}

    def _init_device(self):
        self._device = digitalio.DigitalInOut(self._pin)
        self._device.switch_to_output(value=self._initial_value, drive_mode=self._drive_modes[self._drive_mode])

    def _set_value(self, v):
        self._device.value = self._value = True if v else False
