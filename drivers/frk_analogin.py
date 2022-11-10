from framework import Driver
import analogio

class AnalogIn(Driver):
    _defaults = {'value': 0,
                 'reference_voltage': 0.0}

    _get_set_del = {'value': 'g',
                    'reference_voltage': 'g'}

    def _init_device(self):
        self._device = analogio.AnalogIn(self._pin)
        self._reference_voltage = self._device.reference_voltage
