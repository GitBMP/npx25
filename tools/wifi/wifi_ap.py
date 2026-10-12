import network
import time
from tools import Component


class WiFiAP(Component):
    METADATA = {
        'ssid':   {'type': str,  'label': 'SSID',       'init': True, 'read': True, 'write': True, 'default': 'ESP32-AP', 'widget': 'input'},
        'passwd': {'type': str,  'label': 'Password',    'init': True, 'read': False, 'write': True, 'default': '12345678', 'widget': 'password'},
        'active': {'type': bool, 'label': 'Active',      'read': True, 'write': True, 'widget': 'toggle', 'set': 'set_active'},
        'ip':     {'type': str,  'label': 'IP Address',  'read': True, 'widget': 'text'},
    }

    def __init__(self, ssid='ESP32-AP', passwd='12345678', active=True, name='WiFi AP', **kwargs):
        Component.__init__(self, name, ssid=ssid, passwd=passwd, **kwargs)
        self.ap_if = network.WLAN(network.AP_IF)
        self.set_active(active)
        self.info(f'Initialized as {'' if self.active else 'not '}active')

    def set_active(self, value):
        if value:
            self.ap_if.active(True)
            self.ap_if.config(essid=self.ssid, password=self.passwd)
            t = 0
            while not self.ap_if.active() and t < 50:
                time.sleep(0.1)
                t += 1
            self.info(f'AP started: {self.ssid}, IP: {self.ip()}')
        else:
            self.ap_if.active(False)
            self.info('AP stopped')
        self.active = value
        return True

    def ip(self):
        if self.ap_if.active():
            return self.ap_if.ifconfig()[0]
        return '0.0.0.0'
