from framework import Driver
import keypad

class Buttons(Driver):
    _defaults = {'sleep': 0.01,
                 'value_when_pressed': True,
                 'pull': True,
                 'key_number': None,
                 'pin_alias': None,
                 'pin_name': None,
                 'pressed': False,
                 'released': True,
                 'event': False,
                 'on_pressed': [],
                 'on_released': [],
                 'on_event': []}

    _get_set_del = {'sleep': 'g',
                    'value_when_pressed': 'g',
                    'pull': 'g',
                    'key_number': 'g',
                    'pin_alias': 'g',
                    'pin_name': 'g',
                    'pressed': 'gs',
                    'released': 'gs',
                    'event': 'gs',
                    'on_pressed': 's',
                    'on_released': 's',
                    'on_event': 's'}

    def _init_device(self):
        self._device = keypad.Keys(self._pins, value_when_pressed=self._value_when_pressed, pull=self._pull)

    def _loop(self):
        _event = self._device.events.get()
        if _event:
            if _event.pressed:
                self._pressed = True
                self._released = False
                self._key_number = _event.key_number
                self._pin_alias = self._raw_aliased_pins[_event.key_number][0]
                self._pin_name = self._raw_aliased_pins[_event.key_number][1]
                self._handle_event('pressed', self._pin_alias)
            else:
                self._pressed = False
                self._released = False
                self._handle_event('released')
            self._handle_event('event')
