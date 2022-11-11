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

# imports
import asyncio
import sys
import board
import gc
import atexit

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/framework-circuitpython/framework.git"


class run:
    def __new__(cls, project):
        _project_instance = super(cls.__class__, cls).__new__(cls)
        _project_instance.__init__(project)
        gc.collect()
        asyncio.run(_project_instance._main())

    def __init__(self, project):
        sys.path.insert(0, f'./{project}')
        self._tasks = []
        _configs = self._get_configs()
        self._instantiate_peripherals(_configs)
        self._instantiate_app(project)

    def _get_configs(self):
        return getattr(__import__('conf'), 'conf', None)

    def _instantiate_peripherals(self, configs):
        for alias, options in configs.items():
            driver = options['driver']
            file = f'frk_{driver}'.lower()
            peripheral_instance = getattr(__import__(file), driver, None)()

            for option, value in options.items():
                if option is 'pin' or option is 'pins':
                    self._handle_pins(peripheral_instance, value)
                else:
                    setattr(peripheral_instance, f'_{option}', value)

            peripheral_instance._init_device()
            atexit.register(peripheral_instance.__exit__, None, None, None)
            globals()[alias] = peripheral_instance
            run = getattr(peripheral_instance, '_run', None)
            loop = getattr(peripheral_instance, '_loop', None)
            sleep = getattr(peripheral_instance, '_sleep', 0.01)
            if run:
                task = asyncio.create_task(peripheral_instance._run())
                self._tasks.append(task)
            elif loop:
                task = asyncio.create_task(self._run(loop, sleep))
                self._tasks.append(task)

    def _handle_pins(self, instance, pins):
        sorted_pins = sorted((v, k) for k, v in pins.items())
        instance._raw_aliased_pins = [(k, v) for v, k in sorted_pins]
        instance._aliased_pins = {k: getattr(board, v, None) for k, v in pins.items()}
        if len(pins) == 1:
            instance._pin = getattr(board, list(pins.values())[0], None)
            instance._pins = [instance._pin]
        else:
            instance._pins = [getattr(board, pin, None) for pin in sorted(pins.values())]

    def _instantiate_app(self, project):
        globals()[project] = __import__(project)
        run = getattr(globals()[project], 'run', None)
        setup = getattr(globals()[project], 'setup', None)
        loop = getattr(globals()[project], 'loop', None)
        sleep = getattr(globals()[project], 'sleep', 0.01)
        if run:
            self._tasks.append(run)
        elif setup and loop:
            globals()[project].setup()
            self._tasks.append(self._run(loop, sleep))
        elif setup:
            globals()[project].setup()
        elif loop:
            self._tasks.append(self._run(loop, sleep))

    async def _run(self, func, sleep):
        while True:
            func()
            await asyncio.sleep(sleep)

    async def _main(self):
        await asyncio.gather(*self._tasks)


class Driver:
    def __new__(cls):
        _instance = super(cls.__class__, cls).__new__(cls)
        _defaults = getattr(cls, '_defaults', {})
        _gsd = getattr(cls, '_get_set_del', None)
        for prop, value in _defaults.items():
            setattr(cls, f'_{prop}', value)
            g = s = d = None
            if (_gsd and prop in _gsd and 'g' in _gsd[prop]) or not _gsd:
                g = getattr(cls, f'_get_{prop}', None) or cls._getter(prop)
            if (_gsd and prop in _gsd and 's' in _gsd[prop]) or not _gsd:
                s = getattr(cls, f'_set_{prop}', None) or cls._setter(prop, value)
            if (_gsd and prop in _gsd and 'd' in _gsd[prop]) or not _gsd:
                d = getattr(cls, f'_del_{prop}', None) or cls._deleter(prop)
            setattr(cls, prop, property(g, s, d))
        return _instance

    def _getter(prop):
        return lambda instance: getattr(instance, f'_{prop}', None)

    def _setter(prop, value):
        _prop = f'_{prop}'

        if prop.startswith('on_'):
            event = '_'.join(prop.split('_')[1:])
            def callback_setter(instance, func, event=event):
                instance.register_callback(event, func)
            return callback_setter

        def generic_setter(instance, value, prop=_prop):
            setattr(instance, prop, value)
        def boolean_setter(instance, value, prop=_prop):
            setattr(instance, prop, True) if value else setattr(instance, prop, False)
        def int_setter(instance, value, prop=_prop):
            if isinstance(value, int):
                setattr(instance, prop, value)
            else:
                raise
        def float_setter(instance, value, prop=_prop):
            if isinstance(value, float):
                setattr(instance, prop, value)
            else:
                raise
        def string_setter(instance, value, prop=_prop):
            setattr(instance, prop, str(value))

        setters = {type(True): boolean_setter,
                   type(0): int_setter,
                   type(1.0): float_setter,
                   type('abc'): string_setter}

        try:
            return setters[type(value)]
        except KeyError:
            return generic_setter

    def _deleter(prop):
        return lambda instance: delattr(instance, prop)

    def _init_device(self):
        pass

    def register_callback(self, event, func):
        if callable(func):
            s = getattr(self, f'_on_{event}', None)
            s.append(func)

    def _handle_event(self, *args):
        setattr(self, f'_{args[0]}', True)
        _func_args = args[1:]
        for func in getattr(self, f'_on_{args[0]}', []):
            func(*_func_args)
            setattr(self, f'_{args[0]}', False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if getattr(self, '_device', None):
            try:
                self._device.__exit__(exc_type, exc_val, exc_tb)
            except:
                pass

    def __del__(self):
        self.__exit__(self, None, None, None)
