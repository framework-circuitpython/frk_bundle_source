from framework import Driver
import asyncio

class Delay(Driver):
    _defaults = {'sleep': 0.0,
                 'initial_value': False,
                 'value': False,
                 'delay': 0.5,
                 'start': False,
                 'started': False,
                 'event': False,
                 'on_event': []}

    async def _run(self):
        self._value = self._initital_value
        while True:
            if self._started:
                self._value = not self._value
                self._handle_event('event')
                self._started = False
                _sleep = self._sleep
            elif self._start and not self._started:
                self._start = False
                self._started = True
                _sleep = self._delay
            else:
                _sleep = self._sleep
            await asyncio.sleep(_sleep)
