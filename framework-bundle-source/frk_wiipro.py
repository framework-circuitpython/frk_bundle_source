import asyncio
from busio import I2C
import time

class WiiPro:
    sleep = 0.01
    address = 0x52
    decrypt1 = b'\xF0\x55'
    decrypt2 = b'\xFB\x00'
    data_format = b'\xFE\x03'

    lx = 0 
    ly = 0 
    rx = 0
    ry = 0
    lt = 0
    rt = 0
    bdr = False
    bdd = False
    blt = False
    b_minus = False
    bh = False
    b_plus = False
    brt = False
    bzl = False
    bb = False
    by = False
    ba = False
    bx = False
    bzr = False
    bdl = False
    bdu = False
    
    buttons = {}
    package = {}
    
    event = False
    pressed = False
    released = False
    on_event = []
    on_pressed = []
    on_released = []
        
    def _init_device(self):
        self._buffer = bytearray(8)
        self._i2c.try_lock()
        self._i2c.scan()
        self._i2c.unlock()
    
    async def _run(self):
        self._b = {"bdr": self._bdr,
                   "bdd": self._bdd,
                   "blt": self._blt,
                   "bminus": self._b_minus,
                   "bh": self._bh,
                   "bplus": self._b_plus,
                   "brt": self._brt,
                   "bzl": self._bzl,
                   "bb": self._bb,
                   "by": self._by,
                   "ba": self._ba,
                   "bx": self._bx,
                   "bzr": self._bzr,
                   "bdl": self._bdl,
                   "bdu": self._bdu}
        await asyncio.sleep(0.1)
        self._i2c.try_lock()
        self._i2c.writeto(self._address, self._decrypt1)
        self._i2c.unlock()
        await asyncio.sleep(0.1)
        self._i2c.try_lock()
        self._i2c.writeto(self._address, self._decrypt2)
        self._i2c.unlock()
        await asyncio.sleep(0.1)
        self._i2c.try_lock()
        self._i2c.writeto(self._address, self._data_format)
        self._i2c.unlock()
        await asyncio.sleep(0.1)
        while True:
            try:
                if self._i2c.try_lock():
                    self._i2c.writeto(self._address, b"\x00")
                    time.sleep(0.001)
                    self._i2c.readfrom_into(self._address, self._buffer)
                    self._i2c.unlock()
                    self._decode()
                await asyncio.sleep(self._sleep)
            except:
                pass
    
    def _decode(self):
        self._lx = self._buffer[0]
        self._rx = self._buffer[1]
        self._ly = self._buffer[2]
        self._ry = self._buffer[3]
        self._lt = self._buffer[4]
        self._rt = self._buffer[5]
        self._bdr = not bool(self._buffer[6] & 0x80)
        self._bdd = not bool(self._buffer[6] & 0x40)
        self._blt = not bool(self._buffer[6] & 0x20)
        self._b_minus = not bool(self._buffer[6] & 0x10)
        self._bh = not bool(self._buffer[6] & 0x08)
        self._b_plus = not bool(self._buffer[6] & 0x04)
        self._brt = not bool(self._buffer[6] & 0x02)
        self._bzl = not bool(self._buffer[7] & 0x80)
        self._bb = not bool(self._buffer[7] & 0x40)
        self._by = not bool(self._buffer[7] & 0x20)
        self._ba = not bool(self._buffer[7] & 0x10)
        self._bx = not bool(self._buffer[7] & 0x08)
        self._bzr = not bool(self._buffer[7] & 0x04)
        self._bdl = not bool(self._buffer[7] & 0x02)
        self._bdu = not bool(self._buffer[7] & 0x01)
        
        self._buttons = {"bdr": self._bdr,
                         "bdd": self._bdd,
                         "blt": self._blt,
                         "bminus": self._b_minus,
                         "bh": self._bh,
                         "bplus": self._b_plus,
                         "brt": self._brt,
                         "bzl": self._bzl,
                         "bb": self._bb,
                         "by": self._by,
                         "ba": self._ba,
                         "bx": self._bx,
                         "bzr": self._bzr,
                         "bdl": self._bdl,
                         "bdu": self._bdu}
    
        comp = [k for k, v in self._buttons.items() if v != self._b[k]]
        if comp:
            self._handle_event("event", comp)
            rising = [k for k in comp if not self._b[k] and self._buttons[k]]
            if len(rising) > 0:
                self._handle_event("pressed", rising)
            falling = [k for k in comp if self._b[k] and not self._buttons[k]]
            if len(falling) > 0:
                self._handle_event("released", falling)
            self._b.update(self._buttons)
    
    def _get_package(self):
        return {"lx": self._lx,
                "ly": self._ly,
                "rx": self._rx,
                "ry": self._ry,
                "lt": self._lt,
                "rt": self._rt,
                "bdr": self._bdr,
                "bdd": self._bdd,
                "bblt": self._blt,
                "bminus": self._b_minus,
                "bh": self._bh,
                "bplus": self._b_plus,
                "brt": self._brt,
                "bzl": self._bzl,
                "bb": self._bb,
                "by": self._by,
                "ba": self._ba,
                "bx": self._bx,
                "bzr": self._bzr,
                "bdl": self._bdl,
                "bdu": self._bdu}