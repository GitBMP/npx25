# Workflow

1. **Load sidebar** - `GET /api/sidebar` - None → `[{path, view, ...}, ...]`
2. **Request cards** - `POST /api/cards` 
    - `{"path": "patterns"}` → `[ {"class": "Pattern1", ...} ]`
    - `{"name": "settings"}` → `[ {"setting1": ... } ]`
3. **Poll values** - `POST /api/get` - `["poti.value"]` → `{"poti.value": 5.0}`
4. **Update values** - `POST /api/set` - `{"npx.pin": 2}` → None

------------------------------------------------------------

# 1. Sidebar Loading

**Call**: `GET /api/sidebar` 

**Request**: None

**Response**:
```json
[
    {
        "path": "favourites.dashboard",
        "name": "Dashboard",
        "icon": "icon-home",
        "view": "favourite"
    },
    {
        "path": "favourites.lighting",
        "name": "Lighting Control",
        "icon": "icon-lightbulb",
        "view": "favourite"
    },
    {
        "path": "",
        "icon": "icon-database",
        "view": "container"
    },
    {
        "path": "buttons",
        "icon": "icon-toggle",
        "view": "container"
    },
    { "path": "sensors", "view": "container" },
    { "path": "patterns", "view": "container" },
    {
        "path": "settings",
        "name": "Settings",
        "icon": "icon-settings",
        "view": "utility"
    },
    {
        "path": "logs",
        "name": "Logs",
        "icon": "icon-file-text",
        "view": "utility"
    },
    {
        "path": "system_info",
        "icon": "icon-info",
        "view": "utility"
    }
]
```
- `icon` is optional
- `name` is optional - friendly display name, falls back to last segment of `path` on client
- `view`: `favourite`, `container`, `utility`, or `hide` (hidden from sidebar)
- Client groups by `view` to render sidebar sections

------------------------------------------------------------

# 2. Get Cards

## DataContainer with `path`

**Call**: `POST /api/cards`

**Request**
```json
{ "path": "buttons" }
```

**Response**
```json
[
    {
        "class": "Button",
        "path": "buttons.btn1",
        "pin": {
            "label": "GPIO Pin",
            "value": 1,
            "widget": "number",
            "read": true,
            "write": true,
            "type": "int"
        },
        "pressed": {...}
    },
    {
        "class": "Button",
        "path": "buttons.btn2",
        "pin": {...},
        "pressed": {...}
    }
]
```
- currently no single Class request, just DataContainers

**Favourites Example**
```json
{ "path": "favourites.lighting" } // Request
[
    {
        "class": "NPX",
        "path": "npx",
        "favourite": { "attrs": ["color", "brightness", "pattern"] },
        "color": {...},
        "brightness": {...},
        "pattern": {...}
    },
    {
        "class": "AnalogSensor",
        "path": "sensors.poti",
        "favourite": { "attrs": ["value"] },
        "value": {...}
}   ]
```
- `favourite` as additional Attribute for whitelist information

------------------------------------------------------------

# 3. Get Updates

**Call**: `POST /api/get`

**Request**:
```json
[
    "value",
    "patterns.color.color1",
    "very_long"
]
```
- note: single attr like 'valid' no longer valid
- requests attributes from classes (not classes)

**Response**
```json
{
    "value": 3,
    "patterns.color.color1": [1, 0.5, 0],
    "very_long": {
        "title": "this can be very long",
        "description": "with many items inside"
    }
}
```

------------------------------------------------------------

# 4. Set Values

**Call**: `POST /api/set`

**Request**: 
```json
{
    "value": 5,
    "patterns.color.color1": [0, 0.5, 1],
    "buttons.trigger_callbacks": {},
    "statemachine.transition": {"state_name": "Static"}
}
```

**Response**: `None`

-------------------------------------------------------------------

**Function Call**
- `get` and `set` can call a function 
    - `get` without parameters, with return value
    - `set` with parameters, without return value
- both parameters + return value is not implemented
    - option: make `/api/call` api for that scenario
