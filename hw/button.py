from machine import Pin
import time
from tools import Component, AsyncLoop, Callbacks


class Button(Component, AsyncLoop, Callbacks):
    METADATA = {
        'pin': {'type': int, 'label': 'GPIO Pin', 'init': True, 'read': True, 'write': True, 'min': 0, 'max': 21, 'widget': 'number'},
        'pullup': {'type': bool, 'label': 'Pull-up Resistor', 'init': True, 'read': True, 'write': True, 'default': True, 'widget': 'toggle'},
        'value': {'type': int, 'label': 'Button State', 'read': True, 'widget': 'number', 'min': 0, 'max': 1},
        'duration_ms': {'type': float, 'label': 'Press Duration', 'read': True, 'widget': 'number', 'min': 0, 'unit': 'ms', 'precision': 1},
    }

    def __init__(self, pin, name='Button', loglevel='info', **kwargs):
        AsyncLoop.__init__(self, time=0.1)
        Callbacks.__init__(self)
        Component.__init__(self, name, loglevel, pin=pin, **kwargs)
        self.falling = True
        self.last_falling = 0
        self.duration = 0
        self.button = Pin(self.pin, Pin.IN, Pin.PULL_UP if self.pullup else None)
        self.button.irq(self.irq, Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.info(f'Button: Initialized on pin {self.pin}')

    def set_pin(self, value):
        self.pin = value
        self.button = Pin(self.pin, Pin.IN, Pin.PULL_UP if self.pullup else None)
        self.button.irq(self.irq, Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.info(f'Pin changed to {self.pin}')
        return True

    def set_pullup(self, value):
        self.pullup = value
        self.button = Pin(self.pin, Pin.IN, Pin.PULL_UP if self.pullup else None)
        self.button.irq(self.irq, Pin.IRQ_FALLING | Pin.IRQ_RISING)
        self.info(f'Pull-up changed to {self.pullup}')
        return True

    def irq(self, pin):
        if not pin.value():
            if self.falling:
                self.last_falling = time.time_ns()
                self.falling = False
        else:
            if not self.falling:
                duration = time.time_ns() - self.last_falling
                if duration > 50_000_000:
                    self.duration = duration
                self.falling = True

    def loop(self):
        if self.duration > 0:
            self.debug(f'Button pressed for {self.duration / 1_000_000:.1f}ms')
            self.trigger_callbacks()
            self.duration = 0

    def value(self):
        val = self.button.value()
        if self.t_on:
            self.trace(f'Button state: {val}')
        return val

    def _async_on_resume(self):
        self.duration = 0
        self.falling = True

    def duration_ms(self):
        return self.duration / 1_000_000
