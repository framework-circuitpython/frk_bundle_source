import analogio
import asyncio

class AnalogIn:
    sample_rate = 10000.0
    value = 0
    reference_voltage = 0.0
    
    def _init_device(self):
        self._device = analogio.AnalogIn(self._pin)
        self._sleep = 1.0 / self._sample_rate
    
    async def _run(self):
        while True:
            self._value = self._device.value
            await asyncio.sleep(self._sleep)