
## Meta Attributes Reference

**Defaults** (if not specified):
- `read=True`, `write=False`, `widget='text'`
- Other attributes default to `None` and are omitted from serialization

**Access Control**
- `read` (`bool`): If True, attribute/function can be read (default: `True`)
- `write` (`bool`): If True, attribute/function can be written (default: `False`)

**Widget/Display**
- `widget` (`str`): Widget type for UI rendering (values: `text`, `slider`, `toggle`, `number`, `textarea`, `select`, `button`, `button_row`, `color`)
- `label` (`str`): Display label text shown in UI (ex.: `'Temperature'`)
- `icon` (`str`): Icon name or identifier for UI display (ex.: `'icon-thermometer'`)
- `update` (`bool`): Enable automatic value polling updates (ex.: `True`)

**Value**
- `value` (`any`): Current value of the attribute/function (auto-populated when metadata is fetched)

**Data Type/Validation**
- `type` (`type`): Python type for value validation and conversion (ex.: `int`)
- `min` (`int|float`): Minimum value for numeric validation (ex.: `0`)
- `max` (`int|float`): Maximum value for numeric validation (ex.: `100`)
- `choices` (`list[str]`): List of allowed discrete string values (ex.: `['off', 'low', 'high']`)
- `unit` (`str`): Measurement unit string displayed after value (ex.: `'°C'`)
- `precision` (`int`): Number of decimal places for display/rounding (ex.: `2`)
- `step` (`int|float`): Step increment for numeric input widgets (ex.: `0.1`)

**Path/Structural**
- `name` (`str`): Logical name when different from method name (ex.: `'offset'`)
- `path` (`str`): Short DataContainer path for this component (ex.: `'sensor'`)

**Config/Persistence**
- `config_path` (`str`): JSON config file path for persistence (ex.: `'/sensor.json'`)
- `retain` (`bool`): If True, changes written back to config file (ex.: `True`)

**Documentation**
- `description` (`str`): Human-readable description (ex.: `'Analog input from sensor'`)

**Function/Method Metadata**
- `args` (`dict`): Argument specifications for functions, keys are arg names (ex.: `{'pin': {'widget': 'number', 'min': 0, 'required': True}}`)
- `required` (`bool`): Whether function argument is required (used in args dict) (ex.: `True`)
- `default` (`any`): Default value for function argument (used in args dict) (ex.: `False`)

**Grouping**
- `group` (`str`): Groups multiple entries together in the UI (ex.: `'loop_control'`)

**Widget-Specific**
- `lines` (`int`): Number of lines for textarea widget (ex.: `4`)

**Hidden/Internal** (not serialized)
- `get` (`str`): Internal reference to getter method name (ex.: `'get_pin'`)
- `set` (`str`): Internal reference to setter method name (ex.: `'set_pin'`)

------------------------------------------------------------

# Widget Definitions

**Always Optional (all widgets):**
- `label`, `icon`, `unit`, `description`, `update`

**Access/Structural:**
- `read`, `write`, `path`, `class`, `widget`, `type`, `value`

**Number Attributes:**
- `min`, `max`, `step`
- `precision` (optional)
- Used by: `slider`, `number`

**Choice Attributes:**
- `choices` (list of strings)
- Used by: `select`

**Text Attributes:**
- `lines` (int)
- Used by: `textarea`

------------------------------

## Widget Examples

### `text`
```json
{
    "widget": "text",
    "label": "Status",
    "value": "Running"
}
```
- maybe multiline text (dict, list, str)? 

### `slider`
```json
{
    "widget": "slider",
    "label": "Brightness",
    "value": 0.8,
    "min": 0.0,
    "max": 1.0,
    "step": 0.1
}
```

### `number`
Displays a Input Field with +/- buttons besides it
```json
{
    "widget": "number",
    "label": "GPIO Pin",
    "value": 5,
    "min": 0,
    "max": 21
}
```

### `toggle`
```json
{
    "widget": "toggle",
    "label": "Inverted",
    "value": false
}
```

### `select`
```json
{
    "widget": "select",
    "label": "Mode",
    "value": "medium",
    "choices": ["off", "low", "medium", "high"]
}
```

### `button`
```json
{
    "widget": "button",
    "label": "Trigger",
    "value": "Fire!!!"
}
```

### `textarea`
```json
{
    "widget": "textarea",
    "label": "Config",
    "value": "{\n  \"key\": \"value\"\n}",
    "lines": 4
}
```

### `button_row`
Multiple entries with the same `group` rendered as inline buttons in a single row.
The shared `label` is used as the row label (same label for all group members). 
The `icon` is displayed inside the button.
```json
{
    "widget": "button_row",
    "icon": "icon-play-pause",
    "label": "Async Control",
    "group": "async_control"
}
```
```json
{
    "widget": "button_row",
    "value": "Stop",
    "label": "Async Control",
    "group": "async_control"
}
```

### `keyvalue`
Displays a list of key-value pairs as a vertical list with keys on the left and values on the right.
Uses a list of tuples to preserve order (MicroPython dicts are unordered).
```json
{
    "widget": "keyvalue",
    "label": "Debug Values",
    "value": [["AnalogSensor", 0.523], ["Remapper", 5.23], ["Limiter", 5.23]]
}
```

### `color`
```json
{
    "widget": "color",
    "label": "LED Color",
    "value": [255, 128, 0]
}
```
