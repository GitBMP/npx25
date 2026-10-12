import network
import time
from tools import Component
from tools.mixin import AsyncLoop, Callbacks

IDLE = 0
CONNECTING = 1
CONNECTED = 2
LOST = 3


class WiFiSTA(Component, AsyncLoop, Callbacks):
    METADATA = {
        'ssid':             {'type': str,  'label': 'SSID',             'init': True, 'read': True, 'write': True, 'widget': 'input'},
        'passwd':           {'type': str,  'label': 'Password',          'init': True, 'read': False, 'write': True, 'widget': 'password'},
        'fallback_timeout': {'type': int,  'label': 'Fallback Timeout',  'init': True, 'read': True, 'write': True, 'default': 10, 'widget': 'number', 'min': 1, 'max': 60},
        'active':           {'type': bool, 'label': 'Active',            'read': True, 'write': True, 'widget': 'toggle', 'set': 'set_active'},
        'state':            {'type': str,  'label': 'State',             'read': True, 'widget': 'text'},
        'connected':        {'type': bool, 'label': 'Connected',         'read': True, 'widget': 'toggle'},
        'ip':               {'type': str,  'label': 'IP Address',        'read': True, 'widget': 'text'},
    }

    def __init__(self, ssid, passwd, active=True, name='WiFi STA', **kwargs):
        Component.__init__(self, name, ssid=ssid, passwd=passwd, **kwargs)
        AsyncLoop.__init__(self, time=1)
        Callbacks.__init__(self)
        self.sta_if = network.WLAN(network.STA_IF)
        self._connect_since = None
        self._in_fallback = False
        self.set_active(active)
        self.info(f'Initialized as {'' if self.active else 'not '} active')

    def set_active(self, value):
        self.active = value
        if value:
            self.sta_if.active(True)
            self.connect()
            if not self._running:
                self.async_start()
            self.info(f'Activated STA')
        else:
            self._state = IDLE
            self.sta_if.active(False)
            self.async_stop()
            self.info('Stopped')
            self.info(f'Disabled STA')
        return True

    def connect(self):
        if self.sta_if.isconnected():
            self.sta_if.disconnect()
        self._state = CONNECTING
        self._connect_since = time.ticks_ms()
        self.sta_if.connect(self.ssid, self.passwd)
        self.info(f'Connecting to {self.ssid}')

    def loop(self):
        if self._state == IDLE:
            return

        is_connected = self.sta_if.isconnected()

        if self._state in (CONNECTING, LOST):
            self.time = 1
            if is_connected:
                self._state = CONNECTED
                self._connect_since = None
                self.info(f'Connected: {self.ip()}')
                if self._in_fallback:
                    self._in_fallback = False
                    self.trigger_callbacks(False)
            elif self._connect_since is not None:
                elapsed = time.ticks_diff(time.ticks_ms(), self._connect_since) / 1000
                if elapsed >= self.fallback_timeout and not self._in_fallback:
                    self._in_fallback = True
                    self.warning(f'Fallback triggered after {elapsed:.0f}s')
                    self.trigger_callbacks(True)

        elif self._state == CONNECTED:
            self.time = 5
            if not is_connected:
                self._state = LOST
                self.warning('Connection lost, reconnecting...')
                self.connect()
                if not self._in_fallback:
                    self._in_fallback = True
                    self.trigger_callbacks(True)

    def state(self):
        return self._state

    def connected(self):
        return self.sta_if.isconnected()

    def ip(self):
        if self.sta_if.isconnected():
            return self.sta_if.ifconfig()[0]
        return '0.0.0.0'
