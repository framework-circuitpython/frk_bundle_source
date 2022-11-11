from framework import Driver
import asyncio

class FreeRun(Driver):
    _defaults = {'initial_value': False,
                 'value': False,
                 't_on': 0.5,
                 't_off': 0.5,
                 'event': False,
                 'rising': False,
                 'falling': False,
                 'on_event': [],
                 'on_rising': [],
                 'on_falling': []}

    _get_set_del = {'initial_value': 'g',
                    'value': 'gs',
                    't_on': 'gs',
                    't_off': 'gs',
                    'event': 'gs',
                    'rising': 'gs',
                    'falling': 'gs',
                    'on_event': 's',
                    'on_rising': 's',
                    'on_falling': 's'}

    async def _run(self):
        self._value = self._initial_value
        while True:
            self._value = not self._value
            if self._value:
                self._handle_event('rising', self._value)
                sleep = self._t_on
            else:
                self._handle_event('falling', self._value)
                sleep = self._t_off
            self._handle_event('event', self._value)
            await asyncio.sleep(sleep)
