from framework import Driver
import countio
import digitalio

class EdgeCounter(Driver):
    _defaults = {'sleep': 0.0,
                 'pull': 'UP',
                 'edge': 'FALL',
                 'count': 0,
                 'reset': False,
                 'event': False,
                 'on_event': []}

    _edges = {'RISE': countio.edge.RISE,
              'FALL': countio.edge.FALL,
              'RISE_AND_FALL': countio.edge.RISE_AND_FALL}

    _pulls = {'NONE': None,
              'UP': digitalio.Pull.UP,
              'DOWN': digitalio.Pull.DOWN}

    def _init_device(self):
        self._device = countio.Counter(self._pin, edge=self._edge, pull=self._pull)
        self.__count = self._count = self._device.count

    def _loop(self):
        self._count = self._device.count
        if self._count > self.__count:
            self._handle_event('event', self._count)
            self.__count = self._count

    def _set_reset(self, v):
        if v:
            self._device.reset()
            self.__count = self._count = self._device.count
            self._reset = False
