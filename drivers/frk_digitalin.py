from framework import Driver
import digitalio

class DigitalIn(Driver):
    _defaults = {'sleep': 0.01,
                 'pull': 'UP',
                 'invert': False,
                 'value': False,
                 'event': False,
                 'rising': False,
                 'falling': False,
                 'on_event': [],
                 'on_rising': [],
                 'on_falling': []}

    _get_set_del = {'sleep': 'g',
                    'pull': 'g',
                    'invert': 'gs',
                    'value': 'g',
                    'event': 'gs',
                    'rising': 'gs',
                    'falling': 'gs',
                    'on_event': 's',
                    'on_rising': 's',
                    'on_falling': 's'}

    _pull_modes = {'NONE': None,
                   'UP': digitalio.Pull.UP,
                   'DOWN': digitalio.Pull.DOWN}

    def _init_device(self):
        self._device = digitalio.DigitalInOut(self._pin)
        self._device.switch_to_input(pull=self._pull_modes[self._pull])
        self.__value = self._value = self._device.value ^ self._invert

    def _loop(self):
        self._value = self._device.value ^ self._invert
        if self._value and not self.__value:
            self._handle_event('rising', self._value)
        if not self._value and self.__value:
            self._handle_event('falling', self._value)
        if self._value != self.__value:
            self._handle_event('event', self._value)
            self.__value = self._value
