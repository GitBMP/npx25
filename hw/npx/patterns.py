"""
LED pattern classes for NeoPixel strips.

Usage `Pattern`:
    pattern = Pattern()
    r, g, b = pattern.get_color(0)  # Returns (0, 0, 0)

Usage `Rainbow`:
    pattern = Rainbow(brightness=poti.value, speed=3.0)
    for x in range(50):
        r, g, b = pattern.get_color(x)
        strip.set_pixel(x, r, g, b)

Usage `Static`:
    pattern = Static(color=(1, 0, 0), brightness=poti.value)
    for x in range(50):
        r, g, b = pattern.get_color(x)
        strip.set_pixel(x, r, g, b)

Usage `ColorFade`:
    pattern = ColorFade(color1=(1, 0, 0), color2=(0, 0, 1), brightness=poti.value)
    for x in range(50):
        r, g, b = pattern.get_color(x)
        strip.set_pixel(x, r, g, b)

Usage `RunningLight`:
    pattern = RunningLight(color=(1, 0, 0), background_color=(0, 0, 0), dot_size=3, num_dots=2, brightness=poti.value, speed=5.0)
    for x in range(50):
        r, g, b = pattern.get_color(x)
        strip.set_pixel(x, r, g, b)
"""

import time
from tools import Logger

logger = Logger('Patterns', loglevel='warning')


class Pattern:
    """Base class for LED patterns"""
    def __init__(self):
        self._needs_render = True  # Always render first frame
        self.vars_to_track = []  # Variables to check for changes
        logger.debug(f'{self.__class__.__name__}: Initialized')

    def needs_render(self):
        """Force pattern to re-render on next frame"""
        self._needs_render = True

    def prepare(self) -> bool:
        """
        Prepare pattern for rendering current frame.
        Returns True if pattern has changed and needs re-rendering, False otherwise.

        Note: Variables are compared by reference. In-place modifications are NOT detected:
            pattern.color = [1, 0, 0] # Reassigning triggers re-render
            pattern.color[0] = 0.8  # Won't trigger re-render!

        Or manually trigger re-render:
            pattern.needs_render()
        """
        changed = False
        if self._needs_render:
            self._needs_render = False
            changed = True

        # Check all tracked variables for changes
        
        for var_name in self.vars_to_track:
            value = getattr(self, var_name)
            value = value() if callable(value) else value

            cached_name = f'_{var_name}'
            old_value = getattr(self, cached_name, None)
            setattr(self, cached_name, value)

            if old_value != value:
                changed = True

        return changed

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns RGB tuple (0-1) for LED at position x"""
        return (0.0, 0.0, 0.0)


class Animated(Pattern):
    """Base class for animated patterns that move over time"""
    def __init__(self, speed=None):
        super().__init__()
        self.speed = speed if speed is not None else 0.0
        self.vars_to_track.append('speed')
        self._time_offset = 0.0

    def prepare(self) -> bool:
        """Prepare animated pattern - updates time offset and always needs rendering"""
        super().prepare()
        self._time_offset = (time.ticks_ms() / 1000.0) / self._speed if self._speed != 0 else 0.0
        return True  

    def get_time_offset(self) -> float:
        """Returns cached time offset for current frame"""
        return self._time_offset


class RainbowStatic(Pattern):
    def __init__(self, brightness=None):
        super().__init__()
        self.brightness = brightness if brightness is not None else 1.0
        self.vars_to_track.append('brightness')

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns RGB tuple (0-1) for static rainbow gradient"""
        # No time offset, just position
        position = x / num_leds
        position = position % 1.0  # Wrap around 0-1

        # Direct RGB calculation
        if position < 0.33:
            local_pos = position / 0.33
            r = 1.0 - local_pos
            g = local_pos
            b = 0.0
        elif position < 0.66:
            local_pos = (position - 0.33) / 0.33
            r = 0.0
            g = 1.0 - local_pos
            b = local_pos
        else:
            local_pos = (position - 0.66) / 0.34
            r = local_pos
            g = 0.0
            b = 1.0 - local_pos

        return (r * self._brightness, g * self._brightness, b * self._brightness)


class Rainbow(Animated):
    def __init__(self, brightness=None, speed=None):
        super().__init__(speed)
        self.brightness = brightness if brightness is not None else 1.0
        self.vars_to_track.append('brightness')

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns RGB tuple (0-1) for rainbow with sharp transitions (no plateau at peak)"""
        time_offset = self.get_time_offset()

        # Add time offset to position for animation
        position = (x + time_offset * num_leds) / num_leds
        position = position % 1.0  # Wrap around 0-1

        # Three intervals
        # Interval 1 (0-0.33): Red 1->0, Green 0->1, Blue stays 0
        # Interval 2 (0.33-0.66): Red stays 0, Green 1->0, Blue 0->1
        # Interval 3 (0.66-1.0): Red rises, Blue falls, Green stays 0

        if position < 0.33:
            # Interval 1: Red falls, Green rises
            local_pos = position / 0.33
            r = 1.0 - local_pos
            g = local_pos
            b = 0.0
        elif position < 0.66:
            # Interval 2: Green falls, Blue rises
            local_pos = (position - 0.33) / 0.33
            r = 0.0
            g = 1.0 - local_pos
            b = local_pos
        else:
            # Interval 3: Red rises, Blue falls
            local_pos = (position - 0.66) / 0.34
            r = local_pos
            g = 0.0
            b = 1.0 - local_pos

        return (r * self._brightness, g * self._brightness, b * self._brightness)


class Static(Pattern):
    def __init__(self, color, brightness=None):
        super().__init__()
        self.color = color
        self.brightness = brightness if brightness is not None else 1.0
        self.vars_to_track.append('color')
        self.vars_to_track.append('brightness')

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns static RGB color with brightness applied"""
        r, g, b = self._color
        return (r * self._brightness, g * self._brightness, b * self._brightness)


class ColorFade(Pattern):
    def __init__(self, color1, color2, brightness=None):
        super().__init__()
        self.color1 = color1
        self.color2 = color2
        self.brightness = brightness if brightness is not None else 1.0
        self.vars_to_track.append('color1')
        self.vars_to_track.append('color2')
        self.vars_to_track.append('brightness')

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns RGB color fading from color1 to color2"""
        position = x / (num_leds - 1) if num_leds > 1 else 0

        # Linear interpolation between color1 and color2
        r = self._color1[0] + (self._color2[0] - self._color1[0]) * position
        g = self._color1[1] + (self._color2[1] - self._color1[1]) * position
        b = self._color1[2] + (self._color2[2] - self._color1[2]) * position

        return (r * self._brightness, g * self._brightness, b * self._brightness)


class SoundBar(Pattern):
    def __init__(self, level, color1, color2, brightness=None, inverted=False):
        super().__init__()
        self.level = level
        self.color1 = color1
        self.color2 = color2
        self.brightness = brightness if brightness is not None else 1.0
        self.inverted = inverted
        self.vars_to_track.append('level')
        self.vars_to_track.append('color1')
        self.vars_to_track.append('color2')
        self.vars_to_track.append('brightness')

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns color2 for first level% of LEDs with smooth transition"""
        level = (1.0 - self._level) if self.inverted else self._level
        threshold = level * num_leds

        if x < int(threshold):
            # Fully in color2 zone
            r, g, b = self._color2
        elif x == int(threshold):
            # Transition pixel - blend colors
            blend = threshold - int(threshold)  # fractional part (how much color2)
            r = self._color2[0] * blend + self._color1[0] * (1.0 - blend)
            g = self._color2[1] * blend + self._color1[1] * (1.0 - blend)
            b = self._color2[2] * blend + self._color1[2] * (1.0 - blend)
        else:
            # Fully in color1 zone
            r, g, b = self._color1
        return (r * self._brightness, g * self._brightness, b * self._brightness)


class SoundBarMirror(Pattern):
    def __init__(self, level, color1, color2, brightness=None, inverted=False):
        super().__init__()
        self.level = level
        self.color1 = color1
        self.color2 = color2
        self.brightness = brightness if brightness is not None else 1.0
        self.inverted = inverted
        self.vars_to_track.append('level')
        self.vars_to_track.append('color1')
        self.vars_to_track.append('color2')
        self.vars_to_track.append('brightness')

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns color2 for center level% of LEDs (mirrored) with smooth transition"""
        # Center between middle LEDs for even count (e.g., 3.5 for 8 LEDs)
        center = (num_leds - 1) / 2.0
        distance = abs(x - center)
        level = (1.0 - self._level) if self.inverted else self._level
        threshold = level * num_leds / 2.0  # Half because we fill from center

        if distance < threshold - 0.5:
            # Fully in color2 zone
            r, g, b = self._color2
        elif distance < threshold + 0.5:
            # Transition pixel - blend colors
            blend = 1.0 - (distance - (threshold - 0.5))  # 1.0 at threshold-0.5, 0.0 at threshold+0.5
            r = self._color2[0] * blend + self._color1[0] * (1.0 - blend)
            g = self._color2[1] * blend + self._color1[1] * (1.0 - blend)
            b = self._color2[2] * blend + self._color1[2] * (1.0 - blend)
        else:
            # Fully in color1 zone
            r, g, b = self._color1
        return (r * self._brightness, g * self._brightness, b * self._brightness)


class SoundSlider(Pattern):
    def __init__(self, level, slider_size, color1, color2, brightness=None, inverted=False):
        super().__init__()
        self.level = level
        self.slider_size = slider_size
        self.color1 = color1
        self.color2 = color2
        self.brightness = brightness if brightness is not None else 1.0
        self.inverted = inverted
        self.vars_to_track.append('level')
        self.vars_to_track.append('slider_size')
        self.vars_to_track.append('color1')
        self.vars_to_track.append('color2')
        self.vars_to_track.append('brightness')

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns color1 for slider window at level position with smooth edges"""
        # Calculate slider start position with 0.5 offset (0.0 = start, 1.0 = end)
        level = (1.0 - self._level) if self.inverted else self._level
        slider_start = level * (num_leds - self._slider_size) - 0.5
        slider_end = slider_start + self._slider_size

        if x < slider_start - 0.5:
            # Before slider - color2
            r, g, b = self._color2
        elif x < slider_start + 0.5:
            # Leading edge transition
            blend = x - (slider_start - 0.5)  # 0.0 to 1.0 across the edge
            r = self._color1[0] * blend + self._color2[0] * (1.0 - blend)
            g = self._color1[1] * blend + self._color2[1] * (1.0 - blend)
            b = self._color1[2] * blend + self._color2[2] * (1.0 - blend)
        elif x < slider_end - 0.5:
            # Inside slider - color1
            r, g, b = self._color1
        elif x < slider_end + 0.5:
            # Trailing edge transition
            blend = 1.0 - (x - (slider_end - 0.5))  # 1.0 to 0.0 across the edge
            r = self._color1[0] * blend + self._color2[0] * (1.0 - blend)
            g = self._color1[1] * blend + self._color2[1] * (1.0 - blend)
            b = self._color1[2] * blend + self._color2[2] * (1.0 - blend)
        else:
            # After slider - color2
            r, g, b = self._color2
        return (r * self._brightness, g * self._brightness, b * self._brightness)


class RunningLight(Animated):
    def __init__(self, color, background_color, dot_size=1, num_dots=1, brightness=None, speed=None):
        super().__init__(speed)
        self.color = color
        self.background_color = background_color
        self.dot_size = dot_size
        self.num_dots = num_dots
        self.brightness = brightness if brightness is not None else 1.0
        self.vars_to_track.append('color')
        self.vars_to_track.append('background_color')
        self.vars_to_track.append('dot_size')
        self.vars_to_track.append('num_dots')
        self.vars_to_track.append('brightness')

    def get_color(self, x: int, num_leds: int) -> tuple:
        """Returns color for running light dots moving in a circle"""
        time_offset = self.get_time_offset()

        # Check if LED is within any of the dots
        is_in_dot = False
        for i in range(self._num_dots):
            # Calculate position for each dot (evenly spaced)
            dot_offset = i / self._num_dots
            dot_position = ((time_offset + dot_offset) * num_leds) % num_leds

            # Calculate distance from current LED to this dot center (circular distance)
            distance = abs(x - dot_position)
            # Handle wrap-around for circular strip
            if distance > num_leds / 2:
                distance = num_leds - distance

            # Check if LED is within this dot's size
            if distance < self._dot_size / 2.0:
                is_in_dot = True
                break

        if is_in_dot:
            # Inside a dot
            r, g, b = self._color
        else:
            # Background
            r, g, b = self._background_color

        return (r * self._brightness, g * self._brightness, b * self._brightness)


def hsv_to_rgb(h: float, s: float, v: float) -> tuple:
    h = h / 60.0
    i = int(h) % 6
    f = h - int(h)

    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)

    if i == 0:
        return (v, t, p)
    elif i == 1:
        return (q, v, p)
    elif i == 2:
        return (p, v, t)
    elif i == 3:
        return (p, q, v)
    elif i == 4:
        return (t, p, v)
    else:
        return (v, p, q)
