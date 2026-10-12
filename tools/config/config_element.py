from .helper import evaluate_dict, get_class
from ..mixin import AsyncLoop
from ..data_container import set_nested_path

PENDING = 0
CALLS_PENDING = 1
DONE = 2


class ConfigElement:
    def __init__(self, key, **kwargs):
        self.key = key
        self.class_name = kwargs['class']
        self.values = kwargs.get('values', {})
        self.meta = kwargs.get('meta', {})
        self.calls = kwargs.get('calls', [])
        self.auto_start = kwargs.get('auto_start', True)
        self.instance = None
        self.state = PENDING

    def progress(self):
        if self.state == PENDING:
            if self.try_init():
                self.apply_meta()
                self.state = CALLS_PENDING
                return True
        if self.state == CALLS_PENDING:
            if self.try_calls():
                self.apply_auto_start()
                self.state = DONE
                return True
        return False

    def done(self):
        return self.state == DONE

    def try_init(self):
        cls = get_class(self.class_name)
        try:
            self.instance = cls(**evaluate_dict(self.values))
        except (AttributeError, KeyError, NameError):
            return False
        set_nested_path(self.key, self.instance)
        return True

    def apply_meta(self):
        for attr, overrides in self.meta.items():
            self.instance.meta[attr].update(overrides)

    def try_calls(self):
        try:
            for entry in self.calls:
                func_name, args = next(iter(entry.items()))
                func = getattr(self.instance, func_name)
                func(**evaluate_dict(args))
            return True
        except (AttributeError, KeyError, NameError):
            return False

    def apply_auto_start(self):
        if self.auto_start and isinstance(self.instance, AsyncLoop):
            self.instance.async_start()
