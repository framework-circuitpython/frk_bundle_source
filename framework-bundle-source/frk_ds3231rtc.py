import asyncio
import adafruit_ds3231
import time

class DS3231RTC:
    _days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
    _abreviations = ('MON', 'TUES', 'WED', 'THUR', 'FRI', 'SAT', 'SUN')
    
    sleep = 1.0
    frequency = 100000
    timeout = 255
    calibration = None
    force_temperature_conversion = False
    
    now = None
    year = 0
    month = 0
    day_of_month = 0
    hour = 0
    minute = 0
    second = 0
    day_of_week = 0
    day_of_year = -1
    dst = -1
    temperature = 0
    
    set = None
    
    date = ""
    time = ""
    day = ""
    
    def _init_device(self):
        self._rtc = adafruit_ds3231.DS3231(self._i2c)
        self._temperature = self._rtc.temperature
        t = self._rtc.datetime
        self._now = t
        self._year = int(t.tm_year)
        self._month = int(t.tm_mon)
        self._day_of_month = int(t.tm_mday)
        self._hour = int(t.tm_hour)
        self._minute = int(t.tm_min)
        self._second = int(t.tm_sec)
        self._day_of_week = int(t.tm_wday)
        self._day_of_year = int(t.tm_yday)
        self._dst = int(t.tm_isdst)
        self._date = f'{self.day_of_month}/{self.month}/{self.year}'
        self._time = f'{self.hour:2}:{self.minute:2}:{self.second:2}'
        self._day = self._days[self.day_of_week]
        self._day_abreviation = self._abreviations[self.day_of_week]
    
    async def _run(self):
        while True:
            self._temperature = self._rtc.temperature
            t = self._rtc.datetime
            self._now = t
            self._year = int(t.tm_year)
            self._month = int(t.tm_mon)
            self._day_of_month = int(t.tm_mday)
            self._hour = int(t.tm_hour)
            self._minute = int(t.tm_min)
            self._second = int(t.tm_sec)
            self._day_of_week = int(t.tm_wday)
            self._day_of_year = int(t.tm_yday)
            self._dst = int(t.tm_isdst)
            self._date = f'{self.day_of_month}/{self.month}/{self.year}'
            self._time = f'{self.hour:2}:{self.minute:02d}:{self.second:02d}'
            self._day = self._days[self.day_of_week]
            self._day_abreviation = self._abreviations[self.day_of_week]
            await asyncio.sleep(self._sleep)
    
    def _set_calibration(self, v):
        self._rtc.calibration = v
    
    def _set_set(self, v):
        self._rtc.datetime = time.struct_time(v)