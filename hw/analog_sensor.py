from tools import Component
from machine import Pin, ADC


class AnalogSensor(Component):
    METADATA = {
        'pin': {'type': int, 'label': 'GPIO Pin', 'icon': 'icon-connection', 'init': True, 'read': True, 'write': True, 'min': 0, 'max': 21, 'widget': 'number'},
        'resolution': {'type': int, 'label': 'Resolution', 'icon': 'icon-counter', 'init': True, 'read': True, 'default': 4096, 'widget': 'number'},
        'inverted': {'type': bool, 'label': 'Inverted', 'icon': 'icon-sync', 'init': True, 'read': True, 'write': True, 'default': False, 'widget': 'toggle'},
        'raw_value': {'type': int, 'label': 'Raw Value', 'icon': 'icon-pound-box', 'read': True, 'widget': 'text', 'min': 0, 'max': 4095, 'update': True},
        'value': {'type': float, 'label': 'Value', 'icon': 'icon-counter', 'read': True, 'widget': 'text', 'min': 0.0, 'max': 1.0, 'update': True},
    }

    def __init__(self, pin, name='Analog Sensor', icon='icon-sine-wave', **kwargs):
        Component.__init__(self, name, icon=icon, pin=pin, **kwargs)
        self.sensor = ADC(Pin(pin))
        self.sensor.atten(ADC.ATTN_11DB)
        self.info(f'AnalogSensor: Initialized on pin {pin}')

    def set_pin(self, value):
        self.pin = value
        self.sensor = ADC(Pin(value))
        self.sensor.atten(ADC.ATTN_11DB)
        self.info(f'Pin changed to {value}')
        return True

    def raw_value(self):
        raw = self.sensor.read()
        if self.t_on:
            self.trace(f'Raw ADC reading: {raw}')
        return raw

    def value(self):
        raw = self.raw_value()
        value = raw / self.resolution
        if self.inverted:
            value = 1.0 - value
        if self.t_on:
            self.trace(f'Read value: {value:.3f}')
        return value

    def __str__(self):
        return f'Analog Sensor: {self.value()}'

