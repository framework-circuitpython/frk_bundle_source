from framwork import Driver
import analogio

class AnalogOut(Driver):
    _defaults = {'value': 0}

    _get_set_del = {'value': 'gs'}

    def _init_device(self):
        self._device = analogio.AnalogOut(self._pin)

    def _set_value(self, v):
        self._device.value = self._value = v
