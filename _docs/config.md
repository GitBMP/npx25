# Config System

```json
{
    "poti_raw": {
        "class": "AnalogSensor",
        "logger": "debug",
        "values": { "pin": 2 },
        "meta": { "pin": { "write": false } }
    },
    // dc.poti_raw = AnalogSensor(loglevel='debug', pin=2)
    // dc.poti_raw.meta['pin']['write'] = False

    "poti_smoother": {
        "class": "Smoother",
        "values": { "alpha": 0.3 }
    },

    "poti": {
        "class": "Pipeline",
        "values": { "source": "$poti_raw" },
        "calls": [
            { "add": {"processor": "$poti_smoother" } },
            { "add": {"processor": "$poti_remapper" } }
        ]
    },
    
    "buttons.btn0": {
        "class": "Button",
        "values": { "pin": 1 },
        "calls": [
            { "set_callback": { "fn_callback": "$mode.next" } }
        ]
    }
}
```

```python
ConfigLoader().load('config/')
```
Loads all `.json` files

**Special Files**
- `favourites.json`
- `settings.json`

---

## Keywords

| Key          | Description                                         | Default |
|---|---|---|
| `class`      | Class name (required)                               | —       |
| `values`     | Attribute dict — metadata decides init vs setter    | `{}`    |
| `meta`       | Per-instance metadata overrides                     | `{}`    |
| `calls`      | Ordered list of function calls                      | `[]`    |
| `logger`     | Log level: `trace` `debug` `info` `warning` `error` | `info`  |
| `auto_start` | Call `async_start()` if AsyncLoop                   | `true`  |

---

## values

Sets attributes in the constructor using the class METADATA. 

```json
"sensor": {
    "class": "AnalogSensor",
    "values": { "pin": 2, "inverted": false }
}
```

Only Component-based classes are supported.

---

## calls

A list of single-key dict's. Called from top to bottom

```json
"calls": [
    { "add_state": { "name": "off",    "on_enter": "lambda: $npx.set_pattern($patterns.off)" } },
    { "add_state": { "name": "static", "on_enter": "lambda: $npx.set_pattern($patterns.static)" } }
]
```

---

## meta

Override specific METADATA fields per instance without redefining the whole class metadata:

```json
"sensor": {
    "class": "AnalogSensor",
    "values": { "pin": 2 },
    "meta": { "pin": { "write": false, "widget": "text" } }
}
```

---

## Nested Paths

Dot-notation creates intermediate `DataContainer` entries automatically:

```json. Anything else is a literal string.
"buttons.btn0": { "class": "Button", "values": { "pin": 1 } },
"buttons.btn1": { "class": "Button", "values": { "pin": 4 } }
```

→ `dc.buttons.btn0`, `dc.buttons.btn1`

---

## String Expressions

| Pattern | Behavior |
|---|---|
| `"$ref.path"`                        | Evaluated as Python, `$` → `dc.` |
| `"$a.val + $b.val"`                  | Any expression containing `$` |
| `"lambda: $npx.set_pattern($p.off)"` | Creates callable, `$` substituted inside |
| `"lambda x: x > $threshold.value"`   | Lambda with arguments |
| `"lambda: (func1(), func2())"`       | Multiple calls via tuple trick |
| `"plain string"`                     | Literal — no substitution |

Rules: starts with `$` or `lambda` → evaluated + substitues all `$` to `dc.`.
