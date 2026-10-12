from tools import Component


class Pipeline(Component):
    METADATA = {
        'value': {'type': float, 'label': 'Pipeline Value', 'read': True, 'widget': 'text', 'precision': 3, 'update': True},
        'value_debug': {'type': list, 'label': 'Debug Values', 'read': True, 'widget': 'keyvalue', 'update': True},
    }

    def __init__(self, source, name='Pipeline', loglevel='info', **kwargs):
        Component.__init__(self, name, loglevel, **kwargs)
        self.source = source
        self.processors = []
        self.info(f'Pipeline: Initialized with source {source.name}')

    def add(self, processor):
        self.processors.append(processor)
        self.debug(f'Pipeline: Added {processor.__class__.__name__} (total: {len(self.processors)})')
        return self

    def source_value(self):
        """Reads the source, works for value() methods and value properties"""
        val = self.source.value
        return val() if callable(val) else val

    def value(self):
        val = self.source_value()

        if self.t_on:
            self.trace(f'Pipeline: Source value: {val:.3f}')

        for processor in self.processors:
            val = processor.value(val)

        if self.t_on:
            self.trace(f'Pipeline: Final value: {val:.3f}')

        return val

    def get_layer(self, index):
        return self.processors[index]

    def value_debug(self):
        values = []
        val = self.source_value()
        values.append([self.source.__class__.__name__, val])

        counts = {}
        for processor in self.processors:
            val = processor.value(val)
            cls_name = processor.__class__.__name__
            counts[cls_name] = counts.get(cls_name, 0) + 1
            key = f'{cls_name} {counts[cls_name]}' if counts[cls_name] > 1 else cls_name
            values.append([key, val])

        return values

    def __str__(self):
        return f'Raw: {self.source_value():.3f} | Pipeline: {self.value():.3f}'
