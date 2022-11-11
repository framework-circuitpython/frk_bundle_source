from framework import Driver
import pwmio

class PWMOut(Driver):
    _defaults = {'duty_cycle': 0,
                 'frequency': 500,
                 'variable_frequency': False}

    def _init_device(self):
        self._device = pwmio.PWMOut(self._pin,
                                    duty_cycle=self._duty_cycle,
                                    frequency=self._frequency,
                                    variable_frequency=self._variable_frequency)

    def _set_frequency(self, v):
        if self._variable_frequency:
            self._device.frequency = self._frequency = v

    def _set_duty_cycle(self, v):
        self._device.duty_cycle = self._duty_cycle = v
