import asyncio
import countio
import digitalio

class EdgeCounter:
    sleep = 0.01
    count = 0
    edge = "FALL"
    pull = "NONE"
    reset = False
    alarm_at = 10
    
    alarm = False
    on_alarm = []
    
    _edges = {"RISE": countio.Edge.RISE,
              "FALL": countio.Edge.FALL,
              "RISE_AND_FALL": countio.Edge.RISE_AND_FALL}
    _pulls = {"UP": digitalio.Pull.UP,
              "DOWN": digitalio.Pull.DOWN,
              "NONE": None}
    
    def _init_device(self):
        self._device = countio.Counter(self._pin, edge=self._edges[self._edge], pull=self._pulls[self._pull])
    
    async def _run(self):
        self._count = self._device.count
        while True:
            self._count = self._device.count
            if self._count >= self._alarm_at:
                self._handle_event("alarm")
                self._device.reset()
                self._count = self._device.count
            await asyncio.sleep(self._sleep)
    
    def _set_reset(self, v):
        if v: self._device.reset()