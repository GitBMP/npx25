from ..data_container import DC


def evaluate(value):
    dc = DC()
    if isinstance(value, str):
        if value.startswith('lambda') or value.startswith('$'):
            return eval(value.replace('$', 'dc.'), {'dc': dc})
        return value  # literal string
    elif isinstance(value, list):
        return [evaluate(item) for item in value]
    elif isinstance(value, dict):
        return evaluate_dict(value)
    return value  # int, float, bool, None


def evaluate_dict(d):
    return {key: evaluate(value) for key, value in d.items()}


def get_class(name):
    import hw, tools
    for module in (hw, tools):
        if name in module.__all__:
            return getattr(module, name)
    raise Exception(f'Class not found: {name}')
