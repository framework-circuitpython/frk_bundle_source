import asyncio
import rotaryio

class IncrementalEncoder:
    sleep = 0.01
    divisor = 4
    position = 0
    
    reverse = False
    
    event = False
    increased = False
    decreased = False
    on_event = []
    on_increased = []
    on_decreased = []
    
    def _init_device(self):
        self._device = rotaryio.IncrementalEncoder(*self._pins, divisor=self._divisor)
    
    async def _run(self):
        p = self._position
        while True:
            self._position = self._device.position * {True: -1, False: 1}[self._reverse]
            if self._position != p:
                if self._position > p:
                    self._handle_event("increased", self._position)
                if self._position < p:
                    self._handle_event("decreased", self._position)
                self._handle_event("event", self._position)
                p = self._position
            await asyncio.sleep(self._sleep)