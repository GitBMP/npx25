from .patterns import Pattern
from machine import Pin
import neopixel, time
from tools import Component, AsyncLoop


class NPX(Component, AsyncLoop):
    METADATA = {
        'pin': {'type': int, 'label': 'GPIO Pin', 'init': True, 'read': True, 'min': 0, 'max': 21, 'widget': 'number'},
        'num_leds': {'type': int, 'label': 'Number of LEDs', 'init': True, 'read': True, 'min': 1, 'max': 500, 'widget': 'number'},
        'bpp': {'type': int, 'label': 'Bytes per Pixel', 'init': True, 'read': True, 'default': 3, 'min': 3, 'max': 4, 'widget': 'number'},
        'print_ups_enabled': {'type': bool, 'label': 'Show UPS Counter', 'read': True, 'write': True, 'default': False, 'widget': 'toggle'},
    }

    def __init__(self, pin, num_leds, name='NeoPixel', loglevel='info', **kwargs):
        AsyncLoop.__init__(self, time=0.03)
        Component.__init__(self, name, loglevel, pin=pin, num_leds=num_leds, **kwargs)
        self.zones = []
        self.patterns = []
        self.npx = neopixel.NeoPixel(Pin(self.pin), self.num_leds, bpp=self.bpp)
        self.ups = 0
        self.ups_time = time.time() + 1
        self.info(f'NPX: Initialized on pin {self.pin} with {self.num_leds} LEDs (bpp={self.bpp})')

    def set_print_ups_enabled(self, value):
        self.print_ups_enabled = bool(value)
        return True

    def add_zone(self, size, inverted=False):
        """Adds zone with size LEDs (-1 = all remaining LEDs)"""
        if size == -1:
            used = sum(zone['size'] for zone in self.zones)
            size = self.num_leds - used

        self.zones.append({'size': size, 'inverted': inverted})
        invert_str = ' (inverted)' if inverted else ''
        self.debug(f'NPX: Added zone with {size} LEDs{invert_str} (total zones: {len(self.zones)})')

    def set_pattern(self, pattern, zone=0):
        """Sets pattern for specific zone"""
        # Extend patterns array if needed
        while len(self.patterns) <= zone:
            self.patterns.append(None)
        self.patterns[zone] = pattern
        self.patterns[zone].needs_render()
        self.debug(f'NPX: Set pattern for zone {zone}')

    def loop(self):
        # Use defined zones or default to single zone for all LEDs
        zones = self.zones if len(self.zones) > 0 else [{'size': self.num_leds, 'inverted': False}]

        offset = 0 # zoning offset for other zones
        change = False # if nothing changes don't write

        for zone_idx, zone_dict in enumerate(zones):
            # Variables
            inverted = zone_dict.get('inverted', False)
            size = zone_dict['size']
            

            # Prepare (skip zones without pattern or without changes)
            pattern: Pattern = self.patterns[zone_idx] if zone_idx < len(self.patterns) else None
            if pattern is None or not pattern.prepare():
                offset += size
                continue
            change = True

            # Set Led pattern
            for i in range(size):
                pos = size - i - 1 if inverted else i
                r, g, b = pattern.get_color(pos, size)
                if self.bpp == 3:
                    self.npx[i + offset] = (
                        max(0, min(int(r * 255), 255)),
                        max(0, min(int(g * 255), 255)),
                        max(0, min(int(b * 255), 255)))
                elif self.bpp == 4:
                    self.npx[i + offset] = (
                        max(0, min(int(r * 255), 255)),
                        max(0, min(int(g * 255), 255)),
                        max(0, min(int(b * 255), 255)), 0)
            offset += size
        if change: self.npx.write()

        # Debugging
        if self.t_on:
            self.trace('NPX: Rendering frame')
        if getattr(self, 'print_ups_enabled', False): self._update_ups()
   
    def _update_ups(self):
        """Updates per second counter for debugging"""
        self.ups += 1
        if self.ups_time <= time.time():
            self.info(f'NPX: {self.ups} Updates per second')
            self.ups = 0
            self.ups_time = time.time() + 1

    def enable_ups(self):
        """Enable UPS counter output"""
        self.print_ups_enabled = True
        self.debug('NPX: UPS counter enabled')

    def disable_ups(self):
        """Disable UPS counter output"""
        self.print_ups_enabled = False
        self.debug('NPX: UPS counter disabled')

