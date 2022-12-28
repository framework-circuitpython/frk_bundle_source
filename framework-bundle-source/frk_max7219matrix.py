import busio
import asyncio
import digitalio
from adafruit_max7219 import matrices

class MAX7219Matrix:
    sleep = 0.01
    width = 32
    height = 8
    rotation = 1
    clear_all = False
    pixel = {}
    enable = True
    fill = None
    brightness = 8
    text = {}
    auto_show = True
    
    def _init_device(self):
        self._cs = digitalio.DigitalInOut(self._aliased_pins["CS"])
        self._device = matrices.CustomMatrix(self._spi, self._cs, self._width, self._height, rotation=self._rotation)
    
    def _set_clear_all(self, v):
        if v:
            self._device.clear_all()
            if self._auto_show: self._device.show()
    
    def _set_brightness(self, v):
        if isinstance(v, int) and v >= 0 and v <= 15:
            self._device.brightness = v
            self._brightness = v
            if self._auto_show: self._device.show()
    
    def _set_fill(self, v):
        if v:
            self._device.fill(1)
        else:
            self._device.fill(0)
        if self._auto_show: self._device.show()
    
    def _set_pixel(self, v):
        x = v["x"]
        y = v["y"]
        p = v["p"]
        if p:
            self._device.pixel(x, y, 1)
        else:
            self._device.pixel(x, y, 0)
        if self._auto_show: self._device.show()
    
    def _deinit(self):
        try:
            self._spi.deinit()
            self._cs.deinit()
        except:
            pass