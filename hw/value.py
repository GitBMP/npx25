from tools import Component


class Value(Component):
    METADATA = {
        'value': {'type': object, 'label': 'Value', 'init': True, 'read': True, 'write': True, 'widget': 'text'},
    }

    def __init__(self, value, name='Value', loglevel='info', **meta_overrides):
        Component.__init__(self, name, loglevel, value=value)

        for key, val in meta_overrides.items():
            self.meta['value'][key] = val

        self.info(f'{self.__class__.__name__}: Initialized with value={value}')

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def inc(self):
        meta = self.meta['value']
        choices = meta.get('choices')

        if choices:
            idx = choices.index(self._value)
            self._value = choices[(idx + 1) % len(choices)]
        else:
            step = meta.get('step', 1)
            new_val = self._value + step
            max_val = meta.get('max')
            if max_val is not None:
                new_val = min(new_val, max_val)
            self._value = new_val

    def dec(self):
        meta = self.meta['value']
        choices = meta.get('choices')

        if choices:
            idx = choices.index(self._value)
            self._value = choices[(idx - 1) % len(choices)]
        else:
            step = meta.get('step', 1)
            new_val = self._value - step
            min_val = meta.get('min')
            if min_val is not None:
                new_val = max(new_val, min_val)
            self._value = new_val

    def __str__(self):
        return f'{self.__class__.__name__}: {self.value}'
