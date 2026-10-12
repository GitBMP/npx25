# MicroPython IoT Project - AI Quick Reference

## Project Structure

**Folder Structure:**
- `tools/` - Core system components (logger, pipeline, mixins, state machine, config, data container, webserver, wifi)
- `hw/` - Hardware components (sensors, buttons, LEDs, patterns)
- `app/` - Webserver frontend (HTML/JS/CSS)
- `lib/` - External libraries (microdot)
- `Config/` - Configuration files (WIP - JSON config system under development)
- Leading `_` files/dirs not uploaded to device

**Main Entry:** `main.py` - Direct Python instantiation (no JSON config currently)

**Key Singleton:** `dc = DC()` - Global DataContainer for all instances

## Available Classes

**HW (hw/):**
- `AnalogSensor` - ADC sensor reading (0-1.0 normalized)
- `Button` - Debounced button with callbacks (AsyncLoop + Callbacks)
- `NPX` - NeoPixel controller with pattern support (AsyncLoop)
- **Value** - Universal value wrapper with inc/dec, meta overrides via kwargs
- **Patterns:** `Pattern`, `Animated`, `Rainbow`, `Rainbow2`, `Static`, `ColorFade`, `RunningLight`, `RainbowStatic`

**Tools (tools/):**
- **Logger:** `Logger`, `LoggerManager`
- **Component:** `Component` - Base class with METADATA dict system
- **Data:** `DC`, `DataContainer`
- **Pipeline:** `Pipeline`, `ValueProcessor`, `Smoother`, `SmootherTime`, `Remapper`, `Limiter`, `ToInt`, `Power`, `Inverter`
- **Mixins:** `AsyncLoop`, `Callbacks`
- **State:** `StateMachine`, `State`
- **Web:** `WebServer`, `WiFiBasicAP`, `WiFiBasicSTA`
- **Config (WIP):** `ConfigLoader`, `ConfigElement`, `StringEvaluator`
- **Events:** `EventBus`

## Key Patterns

### DataContainer Pattern
```python
dc = DC()  # singleton - use everywhere

# Direct access
dc.poti = AnalogSensor(pin=2, name='Poti')
dc.npx.set_pattern(pattern)
dc.buttons.btn1.value()

# Nested containers
dc.buttons = DataContainer()
dc.buttons.btn1 = Button(pin=1)
```

### Logger Pattern
```python
# Standalone logger
from tools import Logger
logger = Logger(name='MyClass', loglevel='info')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')

# With trace (expensive calls)
if logger.t_on:
    logger.trace(f'Expensive computation: {heavy_operation()}')

# Available levels: 'trace', 'debug', 'info', 'warning', 'error', 'critical'
```

### Mixin Patterns

**Logger** - Provides logging methods (trace/debug/info/warning/error/critical)
**AsyncLoop** - For continuous/polling tasks (override `loop()`)
**Callbacks** - Event-driven callbacks
```python
class Button(Logger, AsyncLoop, Callbacks):
    def __init__(self, pin, name='Button', loglevel='info'):
        Logger.__init__(self, name, loglevel)
        AsyncLoop.__init__(self, time=0.1)  # 0.1s loop interval
        Callbacks.__init__(self)

        self.pin = pin
        self.pressed = False
        self.info(f'Button: Initialized on pin {pin}')

    def loop(self):
        """AsyncLoop: Called repeatedly to check button state"""
        new_state = self.read_pin()
        if new_state != self.pressed:
            self.pressed = new_state
            if self.pressed:
                self.debug('Button pressed')
                self.trigger_callbacks()  # Callbacks: Fire all registered callbacks

    def value(self):
        """Get current button state"""
        val = self.read_pin()
        if self.t_on:  # Logger: Only trace if enabled (expensive)
            self.trace(f'Button state: {val}')
        return val

# Usage
button = Button(pin=1, name='Power Button')
button.set_callback(lambda: print('Pressed!'))  # Callbacks: Register callback
button.set_callback(my_function)                # Multiple callbacks supported
button.async_start()                            # AsyncLoop: Start background loop
button.async_pause()                            # AsyncLoop: Pause/resume/stop
```

### Pipeline Pattern

Transform sensor values through processor chain:
```python
from tools import Pipeline, Remapper, Limiter, Smoother
from hw import AnalogSensor

# Create sensor
dc.poti_raw = AnalogSensor(pin=2, name='Poti')

# Create pipeline with processors
dc.poti = Pipeline(dc.poti_raw, name='Poti')
dc.poti.add(Smoother(alpha=0.3))  # Smooth readings
dc.poti.add(Remapper(0.05, 0.95, 0.0, 10.0))  # Remap range
dc.poti.add(Limiter(0.0, 10.0))  # Clamp to bounds

# Get processed value
value = dc.poti.value()  # Returns smoothed, remapped, limited value
```

**Available Processors:**
- `Smoother(alpha)` - Exponential moving average (call-rate dependent)
- `SmootherTime(rate)` - Time-based rate limiting
- `Remapper(from_min, from_max, to_min, to_max)` - Range mapping
- `Limiter(min_val, max_val)` - Clamp to bounds
- `ToInt()` - Convert to integer
- `Power(exponent)` - Apply power function
- `Inverter(pivot, scale)` - Invert around pivot

### Value Wrapper Pattern

Single `Value` class for all types, configured via `**meta_overrides`:
```python
from hw import Value

dc.counter = Value(0, type=int, min=0, max=100, step=1, widget='number')
dc.brightness = Value(0.5, type=float, min=0.0, max=1.0, step=0.1, widget='slider')
dc.mode = Value('low', choices=['off', 'low', 'medium', 'high'], widget='select')
dc.color = Value((255, 0, 0), widget='color')

# inc/dec works with step or choices
dc.counter.inc()   # 1
dc.mode.inc()      # 'medium'
dc.mode.dec()      # 'low'
```

### Component Metadata Pattern

Use `Component` base class with `METADATA` dict for web UI and config integration:
```python
from tools import Component

class AnalogSensor(Component):
    METADATA = {
        'pin': {'type': int, 'label': 'GPIO Pin', 'init': True, 'read': True, 'write': True, 'widget': 'number'},
        'resolution': {'type': int, 'label': 'Resolution', 'init': True, 'read': True, 'default': 4096},
        'inverted': {'type': bool, 'label': 'Inverted', 'init': True, 'read': True, 'write': True, 'default': False},
        'value': {'type': float, 'label': 'Value', 'read': True, 'widget': 'slider'},
    }

    def __init__(self, pin, name='Analog Sensor', **kwargs):
        Component.__init__(self, name, pin=pin, **kwargs)
        self.info(f'AnalogSensor: Initialized on pin {pin}')

    def set_pin(self, value):
        self.pin = value
        self.info(f'Pin changed to {value}')
        return True

    def value(self):
        return 0.5
```

**METADATA keys:** `type`, `label`, `widget`, `init`, `read`, `write`, `default`, `min`, `max`, `step`, `choices`, `get`, `set`
- `init`: Attribute is set during `__init__` via `set_init()`
- `read`/`write`: Controls `get_value()`/`set_value()` access
- `get`/`set`: Custom getter/setter function names (defaults to attr_name)
- `Component` inherits from `Logger` + adds `get_meta()`, `set_value()`, `get_value()`, `set_init()`

## MicroPython Constraints

- **No new library imports** without asking first (check MicroPython compatibility)
- **No ABC (Abstract Base Classes)** - use `raise NotImplementedError()` instead
- **All imports at top of file** (except circular dependencies)
- **No `2>NUL` or similar Windows redirects** in bash commands (creates problematic NULL files)

## Testing & Development

- **Test on real hardware** with actual configs - no separate test files needed
- **Cannot run in terminal** - code uses MicroPython libraries and hardware (machine.Pin, neopixel, etc.)
- Files/dirs with leading `_` not uploaded to ESP32
- Main entry: `main.py`

## Component Structure

When adding new components:
- **Location:** Hardware → `hw/`, System tools → `tools/`
- **Inherit from Component** for logging + metadata + path/name attributes (or Logger for logging only)
- **Use trace guards:** `if self.t_on: self.trace(...)`
- **Init log:** `self.info(f'ClassName: Initialized ...')`
- **Define METADATA dict** at class level for web UI / config integration
- **Keep simple** - use mixins (AsyncLoop, Callbacks) for common patterns
- **Update `__init__.py`** in parent package to export new class

## Commenting Style

- **Docstrings:** Only when they add non-obvious information
- One-line preferred: `"""Brief description"""`
- Skip if name/signature is self-explanatory
- **Inline comments:** Very sparse, only for complex logic
- Use `"""` for docstrings, `'` for regular strings
