import asyncio

class FreeRun:
    initial_value = False
    value = False
    t_on = 0.5
    t_off = 0.5
    event = False
    rising = False
    falling = False
    on_event = []
    on_rising = []
    on_falling = []
    
    async def _run(self):
        self._value = self._initial_value
        while True:
            self._value = not self._value
            if self._value:
                self._handle_event('rising')
                sleep = self._t_on
            else:
                self._handle_event('falling')
                sleep = self._t_off
            self._handle_event('event', self._value)
            await asyncio.sleep(sleep)