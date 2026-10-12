"""
Dynamic data container for hierarchical state management with metadata support.

Path concept:
  dc.path = ''
  dc.sensor.path = 'sensor'
  dc.buttons.btn1.path = 'buttons.btn1'

Usage:
    from tools import Logger

    dc = DC()
    dc.poti = AnalogSensor(2)

    # Iterate over items
    for name, obj in dc.items():
        print(name, obj)

    # Get dictionary for webserver
    data = dc.to_dict()
"""

from tools import Logger

logger = Logger('DataContainer', 'info')

class DataContainer:
    def __init__(self, view='container', icon=None, name=None):
        self.path = ''
        self.icon = icon
        self.name = name
        self.view = view
        self._registered = set()
        logger.debug('DataContainer: Initialized')

    def __setattr__(self, name, value):
        """Intercept attribute assignment to track registered items and set paths"""
        super().__setattr__(name, value)
        if not name.startswith('_') and hasattr(self, '_registered'):
            self._registered.add(name)
            if logger.t_on:
                logger.trace(f'DataContainer: Registered \'{name}\'')

            # Auto-set path for objects that have a path attribute
            if hasattr(value, 'path'):
                if self.path:
                    value.path = f'{self.path}.{name}'
                else:
                    value.path = name

    def items(self):
        """Returns all non-private attributes as (name, value) pairs"""
        for name in self._registered:
            if name not in ('path', 'icon', 'name', 'view'):
                yield name, getattr(self, name)

    def get_containers(self):
        """return: [{'path': ''}, {'path': 'buttons', 'icon': 'icon-button'}, {'path': 'foo.bar'}] """
        if self.view != 'hide':
            entry = {'path': self.path, 'view': self.view}
            if self.icon:
                entry['icon'] = self.icon
            if self.name:
                entry['name'] = self.name
            result = [entry]
        else:
            result = []
        for name, value in self.items():
            if isinstance(value, DataContainer):
                result += value.get_containers()
        return result

    def get_cards(self):
        result = []
        for name, item in self.items():
            if hasattr(item, 'get_meta'):
                result.append(item.get_meta())
        return result

    def __str__(self, prefix=''):
        """Tree-like representation similar to Linux tree command"""
        lines = []

        # Get non-private attributes, sorted
        items = [(k, v) for k, v in sorted(self.__dict__.items()) if not k.startswith('_')]

        for i, (key, value) in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = '└── ' if is_last else '├── '
            extension = '    ' if is_last else '│   '

            if isinstance(value, DataContainer):
                # Nested container - recurse
                lines.append(f'{prefix}{connector}{key}:')
                nested_str = value.__str__(prefix + extension)
                if nested_str:  # Only add if nested container has items
                    lines.append(nested_str)
            else:
                # Regular value
                value_str = str(value)
                # If value is long or has newlines, put on next line
                if len(value_str) > 80 or '\n' in value_str:
                    lines.append(f'{prefix}{connector}{key}:')
                    for line in value_str.split('\n'):
                        lines.append(f'{prefix}{extension}    {line}')
                else:
                    lines.append(f'{prefix}{connector}{key}: {value_str}')

        return '\n'.join(lines)

    def __repr__(self):
        """Called when just typing DC() in MicroPython shell"""
        return self.__str__()


class Favourite(DataContainer):
    def __init__(self, icon=None, name=None, cards=None):
        DataContainer.__init__(self, view='favourite', icon=icon, name=name)
        self.cards = cards or []

    def get_cards(self):
        result = []
        for card in self.cards:
            obj = get_nested(card['path'])
            if obj and hasattr(obj, 'get_meta'):
                meta = obj.get_meta()
                if 'attrs' in card:
                    meta['favourite'] = {'attrs': card['attrs']}
                result.append(meta)
        return result

    def set_value(self, value, attr_name):
        if attr_name == 'cards':
            self.cards = value
            logger.info(f'Favourite: Updated cards ({len(value)} cards)')
            return True
        if attr_name == 'add_card':
            if any(c['path'] == value for c in self.cards):
                logger.info(f'Favourite: Card "{value}" already exists')
                return False
            self.cards.append({'path': value})
            logger.info(f'Favourite: Added card "{value}"')
            return True
        logger.warning(f'Favourite: Cannot set "{attr_name}"')
        return False


class DC(DataContainer):
    """Singleton instance of DataContainer for global state management"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DC, cls).__new__(cls)
            DataContainer.__init__(cls._instance)
            cls._instance.path = ''
            cls._instance.settings = DataContainer(view='utility', icon='icon-settings', name='Settings')
            cls._instance.favourites = DataContainer(view='hide')
        return cls._instance

    def __init__(self): pass  # empty to prevent re-initialization


def set_nested_path(path, value, dc=None):
    """Set value at nested path, creating DataContainers as needed

    Example:
        set_nested_path('foo.bar.value', 123, dc)
        # dc.foo.bar.value = 123

        set_nested_path('bar.value_2', my_var2, foo)
        # foo.bar.value_2 = my_var2
    """
    if dc is None:
        dc = DC()

    parts = path.split('.')

    # Navigate/create nested structure
    for part in parts[:-1]:
        if not hasattr(dc, part):
            setattr(dc, part, DataContainer())
        dc = getattr(dc, part)

    # Set final value
    setattr(dc, parts[-1], value)
    return value


def get_nested(path, dc=None):
    """Get value at nested path, returns None if not found"""
    if dc is None:
        dc = DC()
    if path == '':
        return dc
    for part in path.split('.'):
        if hasattr(dc, part):
            dc = getattr(dc, part)
        else:
            return None
    return dc