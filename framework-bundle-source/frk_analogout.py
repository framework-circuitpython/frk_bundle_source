import analogio

class AnalogOut(Driver):
    value = 0

    def _init_device(self):
        self._device = analogio.AnalogOut(self._pin)

    def _set_value(self, v):
        self._device.value = self._value = v
