# SPDX-FileCopyrightText: Copyright (c) 2022 Nathan Woody
#
# SPDX-License-Identifier: MIT
"""
`framework`
================================================================================

Event driven multitasking for Circuitpython


* Author(s): Nathan Woody

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* asyncio

"""

import asyncio
import gc
import board
import busio
import atexit

DEFAULT_SLEEP = 0.01

class run:
    def __new__(cls, *args, start=True, extras={}, handle_extras=None, **kwargs):
        _instance = super(cls.__class__, cls).__new__(cls)
        _instance.__init__(extras, handle_extras, args, kwargs)
        gc.collect()
        if start: asyncio.run(_instance._main())
    
    def __init__(self, extras, handle_extras, args, kwargs):
        self._i2c = []
        self._spi = []
        _configs = kwargs.get("configs") or args[0]
        _app_module = kwargs.get("app") or args[1]
        extras.update({"version_req": self._check_version_req, "boards": self._check_boards})
        _extras = {extra: _configs.pop(extra) for extra in extras if _configs.get(extra)}
        _extras_results = {extra: extras[extra](value) for extra, value in _extras.items()}
        if handle_extras: handle_extras(_extras_results)
        _drivers = {alias: self._build_driver(alias, options, kwargs) for alias, options in _configs.items()}
        self._tasks = [asyncio.create_task(driver._run()) for driver in _drivers.values() if hasattr(driver, "_run")]
        self._build_app(_app_module, _drivers, kwargs)
    
    async def _main(self):
        await asyncio.gather(*self._tasks)
    
    def _check_version_req(self, version_req):
        return version_req
    
    def _check_boards(self, boards):
        pass
    
    def _build_driver(self, alias, options, kwargs):
        driver_class = getattr(__import__(f"frk_{options["driver"]}".lower()), options["driver"])
        if hasattr(driver_class, "_raw_class"):
            driver_instance = driver_class()
            driver_instance._init_driver(alias, options, **kwargs)
        else:
            _flagged_methods = ["_init_device", "_deinit", "_run", "_handle_event"]
            noncalls = {k: v for k, v in driver_class.__dict__.items() if not callable(v) and not k.endswith("__")}
            calls = {k: v for k, v in driver_class.__dict__.items() if callable(v) and not k.endswith("__")}
            flagged_methods = {k: calls.pop(k) for k in _flagged_methods if calls.get(k)}
            class_dict = {k: v for k, v in noncalls.items() if k.startswith("_")}
            defaults = {k: v for k, v in noncalls.items() if not k.startswith("_")}
            callbacks = {"_".join(k.split("_")[1:]): [] for k in noncalls if k.startswith("on_")}
            if callbacks: class_dict["_handle_event"] = flagged_methods.get("_handle_event") or self._make_handle_event()
            getter_methods = {"_".join(k.split("_")[2:]): calls.pop(k) for k, v in calls.items() if k.startswith("_get_")}
            setter_methods = {"_".join(k.split("_")[2:]): calls.pop(k) for k, v in calls.items() if k.startswith("_set_")}
            deleter_methods = {"_".join(k.split("_")[2:]): calls.pop(k) for k, v in calls.items() if k.startswith("_del_")}
            class_dict.update({k: property(getter_methods.get(k) or self._make_getter(k),
                                           setter_methods.get(k) or self._make_setter(k, v),
                                           deleter_methods.get(k) or self._make_deleter(k)) for k, v in defaults.items()})
            class_dict.update(calls)
            defaults.update({k: v for k, v in options.items() if k is not "pin" or k is not "pins"})
            class_dict["__init__"] = self._make_init(defaults, driver_class.__dict__.get("__init__"))
            if "_init_device" in flagged_methods:
                class_dict["_init_device"] = flagged_methods["_init_device"]
                class_dict["_deinit"] = flagged_methods.get("_deinit") or self._make_deinit()
            if "_run" in flagged_methods: class_dict["_run"] = flagged_methods["_run"]
            if driver_class.__dict__.get("__setitem__"): class_dict["__setitem__"] = driver_class.__dict__.get("__setitem__")
            driver_instance = type(f"_{alias}", tuple(), class_dict)()
            driver_instance.alias = alias
            if callbacks: driver_instance._callbacks = callbacks
            if "pin" in options or "pins" in options:
                pins = options.get("pin") or options.get("pins")
                sorted_pins = sorted((v, k) for k, v in pins.items())
                driver_instance._raw_aliased_pins = [(k, v) for v, k in sorted_pins]
                driver_instance._aliased_pins = {k: getattr(board, v) for k, v in pins.items()}
                if len(pins) == 1:
                    driver_instance._pin = getattr(board, list(pins.values())[0])
                else:
                    driver_instance._pins = [getattr(board, pin) for pin in sorted(pins.values())]
            i2c = self._check_i2c(options)
            if i2c: driver_instance._device = driver_instance._i2c = i2c
            spi = self._check_spi(options)
            if spi: driver_instance._device = driver_instance._spi = spi
            if hasattr(driver_instance, "_init_device"):
                driver_instance._init_device()
                atexit.register(driver_instance._deinit)
        #globals()[alias] = driver_instance
        return driver_instance
    
    def _check_i2c(self, options):
        if not options.get("pins"):
            return None
        elif "SCL" not in options["pins"] and "SDA" not in options["pins"]:
            return None
        else:
            SCL = options["pins"]["SCL"]
            SDA = options["pins"]["SDA"]
            frequency = options.get("frequency") or 1000000
            timeout = options.get("timeout") or 255
            for device in self._i2c:
                if device["SCL"] == SCL and device["SDA"] == SDA:
                    return device["device"]
            device = {"device": busio.I2C(getattr(board, SCL), getattr(board, SDA), frequency=frequency, timeout=timeout),
                      "SCL": SCL,
                      "SDA": SDA}
            self._i2c.append(device)
            return device["device"]
    
    def _check_spi(self, options):
        if not options.get("pins"):
            return None
        elif "SCK" not in options["pins"] and "CS" not in options["pins"]:
            return None
        else:
            SCK = options["pins"]["SCK"]
            MOSI = options["pins"].get("MOSI") or "!!!"
            MISO = options["pins"].get("MISO") or "!!!"
            #half_duplex = options.get("half_duplex") or False
            for device in self._spi:
                if device["SCK"] == SCK and (device["MOSI"] == MOSI or device["MISO"] == MISO):
                    return device["device"]
            device = {"device": busio.SPI(getattr(board, SCK), MOSI=getattr(board, MOSI, None), MISO=getattr(board, MISO, None)),
                      "SCK": SCK,
                      "MOSI": MOSI,
                      "MISO": MISO}
            self._spi.append(device)
            return device["device"]
    
    def _make_getter(self, k):
        def getter(obj, _k=f"_{k}"):
            return getattr(obj, _k)
        return getter
    
    def _make_setter(self, k, v):
        if k.startswith("on_"):
            def callback_setter(obj, _v, _k="_".join(k.split("_")[1:])):
                getattr(obj, "_callbacks")[_k].append(_v)
            return callback_setter
        def setter(obj, _v, _k=f"_{k}"):
            setattr(obj, _k, _v)
        return setter
    
    def _make_deleter(self, k):
        def deleter(obj, k=k):
            delattr(obj, k)
        return deleter
    
    def _make_init(self, defaults, user_init):
        def __init__(obj, defaults=defaults, user_init=user_init):
            [setattr(obj, f"_{default}", value) for default, value in defaults.items()]
            if user_init: user_init()
        return __init__
    
    def _make_handle_event(self):
        def _handle_event(obj, *args, **kwargs):
            args = list(args)
            event = args.pop(0)
            setattr(obj, f'_{event}', True)
            for func in getattr(obj, "_callbacks", {}).get(event, []):
                func(*args, **kwargs)
                setattr(obj, f'_{event}', False)
        return _handle_event
    
    def _make_deinit(self):
        def _deinit(obj):
            try:
                obj._device.deinit()
            except:
                print(f"{obj.alias} not deinitialized")
        return _deinit
    
    def _build_app(self, module, drivers, kwargs):
        [setattr(module, name, driver) for name, driver in drivers.items()]
        #globals()["app"] = module
        app_class = getattr(module, str(kwargs.get("app_class_name")), None) or getattr(module, "App", None)
        run = getattr(module, "run", None)
        setup = getattr(module, "setup", None)
        loop = getattr(module, "loop", None)
        sleep = getattr(module, "sleep", None) or kwargs.get("default_sleep") or DEFAULT_SLEEP
        if app_class:
            self._tasks.append(asyncio.create_task(app_class().run()))
        elif run:
            self._tasks.append(asyncio.create_task(module.run()))
        elif hasattr(module, "setup") or hasattr(module, "loop"):
            if hasattr(module, "setup"):
                module.setup()
            if hasattr(module, "loop"):
                async def run(loop=loop, sleep=sleep):
                    while True:
                        loop()
                        await asyncio.sleep(sleep)
                module.run = run
                self._tasks.append(asyncio.create_task(run()))