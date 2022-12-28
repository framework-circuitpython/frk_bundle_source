import keypad
import asyncio

class Buttons:
    sleep = 0.01
    value_when_pressed = True
    pull = True
    
    key_number = None
    pin_alias = None
    pin_name = None
    
    event = False
    pressed = False
    released = False
    on_event = []
    on_pressed = []
    on_released = []
    
    def _init_device(self):
        self._device = keypad.Keys(self._pins, value_when_pressed=self.value_when_pressed, pull=self.pull)
    
    async def _run(self):
        while True:
            event = self._device.events.get()
            if event:
                if event.pressed:
                    self._pressed = True
                    self._released = False
                    self._key_number = event.key_number
                    self._pin_alias = self._raw_aliased_pins[event.key_number][0]
                    self._pin_name = self._raw_aliased_pins[event.key_number][1]
                    self._handle_event("pressed", self._pin_alias)
                else:
                    self._pressed = False
                    self._released = True
                    self._key_number = event.key_number
                    self._pin_alias = self._raw_aliased_pins[event.key_number][0]
                    self._pin_name = self._raw_aliased_pins[event.key_number][1]
                    self._handle_event("released", self._pin_alias)
                self._handle_event("event", self._pin_alias)
            await asyncio.sleep(self._sleep)