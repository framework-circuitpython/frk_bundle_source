from framework import Driver
import rotaryio

class IncrementalEncoder(Driver):
    _defaults = {'divisor': 2,
                 'reverse': False,
                 'position': 0,
                 'event': False,
                 'increased': False,
                 'decreased': False,
                 'on_event': [],
                 'on_incresed': [],
                 'on_decreased': []}

    def _init_device(self):
        self._device = rotaryio.IncrementalEncoder(*self._pins, divisor=self._divisor)
        self.__position = self._position = self._device.position

    def _loop(self):
        self._position = self._device.position * {True: -1, False: 1}[self._reverse]
        if self.__position < self._position:
            self._handle_event('increased', self._position)
        if self.__position > self._position:
            self._handle_event('decreased', self._position)
        if self.__position != self._position:
            self._handle_event('event', self._position)
