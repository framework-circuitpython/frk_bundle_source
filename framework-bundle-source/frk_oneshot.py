import asyncio

class OneShot:
    sleep = 0
    initial_value = False
    enable = True
    t_on = 0.1
    
    value = False
    start = False
    started = False
    
    event = False
    rising = False
    falling = False
    on_event = []
    on_rising = []
    on_falling = []
    
    async def _run(self):
        sleep = self._sleep
        v = self._value = self._initial_value
        while True:
            if self._enable:
                if self._started:
                    self._value = not self._value
                    self._started = False
                    sleep = self._sleep
                elif self._start and not self._started:
                    self._value = not self._value
                    self._started = True
                    self._start = False
                    sleep = self._t_on
                else:
                    sleep = self._sleep
            if self._value != v:
                if self._value:
                    self._handle_event("rising")
                else:
                    self._handle_event("falling")
                self._handle_event("event", self._value)
                v = self._value
            await asyncio.sleep(sleep)