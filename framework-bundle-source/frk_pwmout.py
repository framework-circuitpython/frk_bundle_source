import pwmio
import asyncio

class PWMOut:
    variable_frequency = False
    frequency = 500
    duty_cycle = 0
    value = 0
    sleep = 0.1
    
    def _init_device(self):
        self._device = pwmio.PWMOut(self._pin,
                                    duty_cycle=self._duty_cycle,
                                    frequency=self._frequency,
                                    variable_frequency=self._variable_frequency)
    
    async def _run(self):
        _variable_frequency = self._variable_frequency
        while True:
            if _variable_frequency != self._variable_frequency:
                self._init_device()
                _variable_frequency = self._variable_frequency
            await asyncio.sleep(self._sleep)
    
    def _set_frequency(self, v):
        if self._variable_frequency:
            self._frequency = v
    
    def _set_duty_cycle(self, v):
        self._device.duty_cycle = self._duty_cycle = self._value = v
    
    def _set_value(self, v):
        self._device.duty_cycle = self._duty_cycle = self._value = v