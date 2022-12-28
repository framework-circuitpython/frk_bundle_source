import asyncio
from digitalio import DigitalInOut, Pull

class DigitalIn:
    poll_rate = 50.0
    value = False
    pull = "UP"
    invert = False
    enable = True
    event = False
    rising = False
    falling = False
    on_event = []
    on_rising = []
    on_falling = []
    
    _pulls = {"NONE": None,
              "UP": Pull.UP,
              "DOWN": Pull.DOWN}
    
    def _init_device(self):
        self._device = DigitalInOut(self._pin)
        self._device.switch_to_input(pull=self._pulls[self._pull])
        self._value = self._previous = self._device.value
        self._sleep = 1.0 / self._poll_rate
    
    def _run(self):
        while True:
            self._value = self._device.value ^ self._invert & self._enable
            if self._value != self._previous:
                self._handle_event('event', self._value)
                if self._value:
                    self._handle_event('rising')
                else:
                    self._handle_event('falling')
                self._previous = self._value
            await asyncio.sleep(self._sleep)