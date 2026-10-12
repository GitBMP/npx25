"""
Value processor classes for transforming sensor values.

Usage `Smoother`:
    from tools import Logger

    pipeline = Pipeline(sensor)
    pipeline.add(Smoother(alpha=0.2, logger=Logger('Smoother')))

Usage `SmootherTime`:
    pipeline = Pipeline(sensor)
    pipeline.add(SmootherTime(rate=0.5))

Usage `Remapper`:
    pipeline = Pipeline(sensor)
    pipeline.add(Remapper(from_min=0.25, from_max=0.9, to_min=0.0, to_max=1.0))

Usage `Limiter`:
    pipeline = Pipeline(sensor)
    pipeline.add(Limiter(min_val=0.1, max_val=0.9))

Usage `ToInt`:
    pipeline = Pipeline(sensor)
    pipeline.add(ToInt())  # Converts float to int (e.g., for color indices)

Usage `Power`:
    pipeline = Pipeline(sensor)
    pipeline.add(Power(exponent=2.0))  # Quadratic curve for brightness control

Usage `Inverter`:
    pipeline = Pipeline(poti)
    pipeline.add(Inverter())  # Inverts: 0→1, 1→0
    pipeline.add(Inverter(pivot=0.5))  # Mirrors around 0.5
"""

import time
from tools import Logger

logger = Logger('Processor', 'info')


class ValueProcessor:
    def __init__(self):
        logger.debug(f'{self.__class__.__name__}: Initialized')

    def value(self):
        """Override this method to implement processing logic"""
        raise NotImplementedError('Subclass must implement value() method')


class Smoother(ValueProcessor):
    """
    Smooths noisy readings using exponential moving average.
    Input: float or int with noise
    Output: smoothed float

    WARNING: Call-rate dependent! Alpha should be tuned for your update frequency.
    - For 1 Hz updates: alpha=0.3 gives moderate smoothing
    - For 60 Hz updates: alpha=0.05 gives similar smoothing

    Lower alpha = more smoothing, higher alpha = more responsive
    """
    def __init__(self, alpha=0.5):
        ValueProcessor.__init__(self)
        self.alpha = alpha
        self.last_value = 0.0

    def value(self, val):
        """Returns smoothed value using exponential moving average"""
        self.last_value = self.alpha * val + (1 - self.alpha) * self.last_value
        return self.last_value


class SmootherTime(ValueProcessor):
    """
    Time-based smoother with rate limiting.
    Input: float or int
    Output: smoothed float that changes at maximum rate per second

    Rate: maximum change per second (e.g., rate=0.5 means 0→1 takes 2 seconds)
    Independent of call frequency - same behavior at 1Hz or 60Hz
    """
    def __init__(self, rate=1.0):
        ValueProcessor.__init__(self)
        self.rate = rate
        self.last_value = None
        self.last_time = time.time_ns()

    def value(self, val):
        """Returns smoothed value with time-based rate limiting"""
        current_time = time.time_ns()

        if self.last_value is None:
            self.last_value = val
            self.last_time = current_time
            return self.last_value

        dt = (current_time - self.last_time) / 1_000_000_000
        max_change = self.rate * dt

        diff = val - self.last_value
        if abs(diff) <= max_change:
            self.last_value = val
        elif diff > 0:
            self.last_value += max_change
        else:
            self.last_value -= max_change

        self.last_time = current_time
        return self.last_value


class Remapper(ValueProcessor):
    """
    Remaps value from one range to another range.
    Input: float or int in range [from_min, from_max]
    Output: float in range [to_min, to_max]
    Example: sensor reads 0.2-0.95, remap to 0.0-1.0 for full range

    Supports dynamic parameters via callables (lambda functions):
    - from_min, from_max, to_min, to_max can be static values or callables
    - If callable, they are evaluated on each call to value()
    """
    def __init__(self, from_min, from_max, to_min=0.0, to_max=1.0):
        ValueProcessor.__init__(self)
        self.from_min = from_min
        self.from_max = from_max
        self.to_min = to_min
        self.to_max = to_max

    def value(self, val):
        """Returns value remapped from one range to another"""
        # Resolve parameters (call if callable, otherwise use directly)
        from_min = self.from_min() if callable(self.from_min) else self.from_min
        from_max = self.from_max() if callable(self.from_max) else self.from_max
        to_min = self.to_min() if callable(self.to_min) else self.to_min
        to_max = self.to_max() if callable(self.to_max) else self.to_max

        normalized = (val - from_min) / (from_max - from_min)
        return to_min + normalized * (to_max - to_min)


class Limiter(ValueProcessor):
    """
    Clamps value to stay within min/max bounds.
    Input: float or int
    Output: float or int (same type as min/max), clamped between [min_val, max_val]
    Prevents values from going out of valid range

    Supports dynamic parameters via callables (lambda functions):
    - min_val, max_val can be static values or callables
    - If callable, they are evaluated on each call to value()
    """
    def __init__(self, min_val=0.0, max_val=1.0):
        ValueProcessor.__init__(self)
        self.min_val = min_val
        self.max_val = max_val

    def value(self, val):
        """Returns value clamped between min_val and max_val"""
        # Resolve parameters (call if callable, otherwise use directly)
        min_val = self.min_val() if callable(self.min_val) else self.min_val
        max_val = self.max_val() if callable(self.max_val) else self.max_val
        return max(min_val, min(max_val, val))


class ToInt(ValueProcessor):
    """
    Converts value to integer.
    Input: float or int
    Output: int (uses floor rounding)
    Useful for color indices, discrete states, or array indexing
    """
    def __init__(self):
        ValueProcessor.__init__(self)

    def value(self, val):
        """Returns value converted to integer"""
        return int(val)


class Power(ValueProcessor):
    """
    Applies power function (x^exponent) for non-linear curves.
    Input: float in range [0.0, 1.0]
    Output: float in range [0.0, 1.0]

    Exponent effects (for brightness control):
    - exponent = 1.0: Linear, no change
    - exponent > 1.0: More control at low values (e.g., 2.0 gives quadratic)
    - exponent < 1.0: More control at high values (e.g., 0.5 gives square root)
    - exponent = 4.0: Very fine control at low end, abrupt at high end

    Example: brightness = Value(0.5, 0.0, 1.0, 0.1, 0.1)
             pipeline = Pipeline(brightness)
             pipeline.add(Power(exponent=2.0))  # Quadratic brightness curve
    """
    def __init__(self, exponent=2.0):
        ValueProcessor.__init__(self)
        self.exponent = exponent

    def value(self, val):
        """Returns val^exponent"""
        return val ** self.exponent


class Inverter(ValueProcessor):
    """
    Inverts value around a pivot point with optional scaling.
    Input: float or int
    Output: scale * (pivot - val)

    Supports dynamic parameters via callables (lambda functions):
    - pivot, scale can be static values or callables
    - If callable, they are evaluated on each call to value()

    Examples:
    - Inverter(): Does 1.0 - x (default inversion)
    - Inverter(pivot=0.5): Mirrors around 0.5 (input 0→0.5, input 1→-0.5)
    - Inverter(scale=-1.0): Does -1.0 * (1.0 - x) = x - 1.0
    - Inverter(pivot=1.0, scale=2.0): Does 2.0 * (1.0 - x)

    Common use case: Inverting potentiometer (0→1 becomes 1→0)
    """
    def __init__(self, pivot=1.0, scale=1.0):
        ValueProcessor.__init__(self)
        self.pivot = pivot
        self.scale = scale

    def value(self, val):
        """Returns scale * (pivot - val)"""
        # Resolve parameters (call if callable, otherwise use directly)
        pivot = self.pivot() if callable(self.pivot) else self.pivot
        scale = self.scale() if callable(self.scale) else self.scale
        return scale * (pivot - val)
