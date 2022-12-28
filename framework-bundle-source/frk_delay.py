import asyncio

class Delay:
    sleep = 0
    initial_value = False
    value = False
    t_delay = 1.0
    
    start = False
    started = False
    
    event = False
    on_event = []
    
    async def _run(self):
        self._value = self._initial_value
        while True:
            if self._started:
                self._value = not self._value
                self._handle_event("event", self._value)
                self._started = False
                sleep = self._sleep
            elif self._start and not self._started:
                self._start = False
                self._started = True
                sleep = self._t_delay
            else:
                sleep = self._sleep
            await asyncio.sleep(sleep)