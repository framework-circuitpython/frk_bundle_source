from framework import Driver
import asyncio

class OneShot(Driver):
    _defaults = {'sleep': 0.0,
                 'initial_value': False,
                 'value': False,
                 'enable': True,
                 't_on': 0.1,
                 'start': False,
                 'started': False,
                 'event': False,
                 'rising': False,
                 'falling': False,
                 'on_event': [],
                 'on_rising': [],
                 'on_falling': []}

    async def _run(self):
        _sleep = self._sleep
        self.__value = self._value = self._initial_value
        while True:
            if self._enable:
                if self._started:
                    self._value = not self._value
                    self._started = False
                    _sleep = self._sleep
                elif self._start and not self._started:
                    self._value = not self._value
                    self._started = True
                    self.start = False
                    _sleep = self._t_on
                else:
                    _sleep = self._sleep

                if self._value and not self.__value:
                    self._handle_event('rising')
                if not self._value and self.__value:
                    self._handle_event('falling')
                if self._value != self.__value:
                    self._handle_event('event')
                    self.__value = self._value
            await asyncio.sleep(_sleep)
