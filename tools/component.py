"""
Component base class with logging and dict-based metadata support.

Usage:
    class AnalogSensor(Component):
        METADATA = {
            'pin': {'type': int, 'label': 'GPIO Pin', 'init': True, 'read': True},
            'value': {'type': float, 'label': 'Value', 'read': True},
        }

        def __init__(self, pin, name='Sensor', **kwargs):
            Component.__init__(self, name)
            self.set_init(pin=pin, **kwargs)

        def value(self):
            return 0.5
    
    sensor = AnalogSensor(3, name='Poti', resolution=1024)
    sensor.get_value('pin')          # 3
    sensor.set_value(5, 'pin')       # calls set_pin(5)
    sensor.get_value('value')        # calls value() -> 0.5
    sensor.get_meta()                # returns all metadata with current values

    # Override instance metadata at runtime
    sensor.meta['value']['widget'] = 'number'
    sensor.meta['value']['precision'] = 3
"""

from .logger import Logger


class Component(Logger):
    """Base class providing logging, naming, path tracking, and metadata."""

    METADATA = {}

    def __init__(self, name='Component', loglevel='info', icon=None, **kwargs):
        Logger.__init__(self, name, loglevel)
        merged = {}
        self._collect_metadata(type(self), merged)
        self.meta = {k: v.copy() for k, v in merged.items()}
        self.meta['class'] = type(self).__name__
        self.icon = icon
        self.set_init(**kwargs)

    def _collect_metadata(self, cls, merged):
        """Walk __bases__ depth-first, bases first so subclass wins."""
        for base in cls.__bases__:
            self._collect_metadata(base, merged)
        if 'METADATA' in cls.__dict__:
            merged.update(cls.METADATA)

    def set_init(self, **kwargs):
        """Set all init attributes from kwargs, using METADATA defaults."""
        for attr_name, metadata in self.meta.items():
            if not isinstance(metadata, dict):
                continue
            if not metadata.get('init', False):
                continue

            if attr_name in kwargs:
                value = kwargs[attr_name]
            elif 'default' in metadata:
                value = metadata['default']
            else:
                raise ValueError(f'Required init parameter "{attr_name}" not provided and has no default')

            converted = self.convert_type(value, metadata)
            if not self.validate_value(converted, metadata):
                raise ValueError(f'Validation failed for init parameter "{attr_name}"')

            setter_name = metadata.get('set', attr_name)
            setter = getattr(self, setter_name, None)

            if callable(setter):
                setter(converted)
            else:
                setattr(self, setter_name, converted)

    def set_value(self, value, attr_name):
        """Set attribute value with validation and type conversion."""
        metadata = self.meta.get(attr_name)
        if not isinstance(metadata, dict):
            self.warning(f'set_value: Attribute "{attr_name}" does not exist')
            return False

        if not metadata.get('write', False):
            self.warning(f'set_value: Attribute "{attr_name}" cannot be written')
            return False

        if metadata.get('widget') in ('button', 'button_row'):
            action_name = metadata.get('set', attr_name)
            action = getattr(self, action_name, None)
            if callable(action):
                try:
                    action()
                    return True
                except Exception as e:
                    self.warning(f'set_value: Action call failed for "{attr_name}": {e}')
                    return False
            self.warning(f'set_value: Action "{action_name}" not found')
            return False

        converted_value = self.convert_type(value, metadata)

        if not self.validate_value(converted_value, metadata):
            self.warning(f'set_value: Validation failed for "{attr_name}"')
            return False

        setter_name = metadata.get('set', attr_name)
        setter = getattr(self, setter_name, None)

        if callable(setter):
            try:
                return setter(converted_value)
            except Exception as e:
                self.warning(f'set_value: Setter call failed for "{attr_name}": {e}')
                return False

        setattr(self, setter_name, converted_value)
        return True

    def get_value(self, attr_name):
        """Get attribute value or None if not found."""
        metadata = self.meta.get(attr_name)
        if not isinstance(metadata, dict):
            self.warning(f'get_value: Attribute "{attr_name}" does not exist')
            return None

        if not metadata.get('read', True):
            self.warning(f'get_value: Attribute "{attr_name}" cannot be read')
            return None

        getter_name = metadata.get('get', attr_name)
        attr = getattr(self, getter_name, None)

        if callable(attr):
            try:
                return attr()
            except Exception as e:
                self.warning(f'get_value: Getter call failed for "{attr_name}": {e}')
                return None

        return attr

    def get_meta(self):
        """Get metadata dict with current values, JSON-safe."""
        for attr_name, metadata in self.meta.items():
            if attr_name in ['class', 'path', 'icon']:
                continue
            if metadata.get('read', True):
                metadata['value'] = self.get_value(attr_name)

        if self.path:
            self.meta['path'] = self.path

        if self.icon:
            self.meta['icon'] = self.icon

        # Build JSON-safe copy: convert type objects to name strings
        result = {}
        for key, val in self.meta.items():
            if not isinstance(val, dict):
                result[key] = val
                continue
            safe = {}
            for k, v in val.items():
                if k == 'type' and isinstance(v, type):
                    safe[k] = v.__name__
                else:
                    safe[k] = v
            result[key] = safe

        return result

    def convert_type(self, value, metadata):
        """Convert value to the specified type."""
        target_type = self.resolve_type(metadata.get('type', object))
        if target_type is None:
            return value

        try:
            if target_type == bool:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == str:
                return str(value)
        except (ValueError, TypeError) as e:
            self.warning(f'convert_type: Failed to convert {value} to {target_type.__name__}: {e}')

        return value

    def validate_value(self, value, metadata):
        """Validate value against metadata constraints."""
        target_type = self.resolve_type(metadata.get('type', object))
        if target_type is not None and target_type is not object and not isinstance(value, target_type):
            self.warning(f'Value {value} is not of type {target_type.__name__}')
            return False

        min_val = metadata.get('min')
        if min_val is not None and value < min_val:
            self.warning(f'Value {value} below minimum {min_val}')
            return False

        max_val = metadata.get('max')
        if max_val is not None and value > max_val:
            self.warning(f'Value {value} above maximum {max_val}')
            return False

        choices = metadata.get('choices')
        if choices is not None and value not in choices:
            self.warning(f'Value {value} not in choices {choices}')
            return False

        return True

    TYPE_MAP = {'int': int, 'float': float, 'str': str, 'bool': bool}
    def resolve_type(self, target_type: 'type | str') -> type:
        if isinstance(target_type, type):
            return target_type
        if isinstance(target_type, str) and target_type in Component.TYPE_MAP:
            return Component.TYPE_MAP[target_type]
        self.warning(f'Unknown type for {target_type}')
        return None