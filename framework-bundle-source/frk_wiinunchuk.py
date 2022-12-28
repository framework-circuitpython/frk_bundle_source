import asyncio
from busio import I2C
import time
from math import atan2, degrees, sqrt

class WiiNunchuk:
    sleep = 0.01
    address = 0x52
    decrypt1 = b'\xF0\x55'
    decrypt2 = b'\xFB\x00'
    data_format = b'\xFE\x03'
    
    x = 0 #8 bit
    y = 0 #8 bit
    ax = 0 #10 bit
    ay = 0 #10 bit
    az = 0 # 10 bit
    c = False
    z = False
    buttons = {}
    package = {}
    tilt = tuple()
    
    def _init_device(self):
        self._buffer = bytearray(8)
        self._i2c.try_lock()
        self._i2c.scan()
        self._i2c.unlock()
    
    async def _run(self):
        self._b = {"c": self._c,
                   "z": self._z}
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
        self._x = int(self._buffer[0])
        self._y = int(self._buffer[1])
        self._joystick = (self._x, self._y)
        self._ax = ((self._buffer[5] & 0xC0) >> 6) | (self._buffer[2] << 2)
        self._ay = ((self._buffer[5] & 0x30) >> 4) | (self._buffer[3] << 2)
        self._az = ((self._buffer[5] & 0x0C) >> 2) | (self._buffer[4] << 2)
        self._accelerometer = (self._ax, self._ay, self._az)
        self._c = not bool(self._buffer[5] & 0x02)
        self._z = not bool(self._buffer[5] & 0x01)
        self._buttons = (self._c, self._z)
        
        self._buttons = {"c": self._c,
                         "z": self._z}
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
        return {
            "x": self._x,
            "y": self._y,
            "ax": self._ax,
            "ay": self._ay,
            "az": self._az,
            "c": self._c,
            "z": self._z
        }
    
    def _get_tilt(self):
        x = self._ax - 2**9
        y = self._ay - 2**9
        z = self._az - 2**9
        theta = atan2(x, sqrt(y**2 + z**2))
        psi = atan2(y, sqrt(x**2 + z**2))
        phi = atan2(z, sqrt(x**2 + y**2))
        return degrees(theta), -(degrees(psi) - 8.0), -(degrees(phi) - 90.0)