function createCardItem(item) {
    const dataPath = item.dataPath;
    const isReadonly = !item.write;

    // Separator
    if (item.widget === 'separator') {
        const hr = document.createElement('hr');
        hr.className = 'card-separator';
        return hr;
    }

    // If widget is defined, handle special cases
    if (item.widget) {
        return createWidgetRow(item, dataPath, isReadonly);
    }

    // Default: simple row with label + optional value
    const row = document.createElement('div');
    row.className = 'card-row';

    // Left side: label with optional icon
    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    row.appendChild(label);

    // Right side: value (if exists)
    if (item.value !== undefined) {
        const value = document.createElement('span');
        value.className = 'row-value';
        value.textContent = item.value + (item.unit || '');
        row.appendChild(value);

        // Register for updates if needed
        if (item.update && dataPath) {
            registerForUpdates(dataPath, (newValue) => {
                value.textContent = newValue + (item.unit || '');
            });
        }
    }

    return row;
}

function createWidgetRow(item, dataPath, isReadonly) {
    switch(item.widget) {
        case 'text':
            return createTextRow(item, dataPath);
        case 'input':
            return createInputRow(item, dataPath, isReadonly);
        case 'password':
            return createPasswordRow(item, dataPath, isReadonly);
        case 'toggle':
            return createToggleRow(item, dataPath, isReadonly);
        case 'slider':
            return createSliderRow(item, dataPath, isReadonly); // Returns ARRAY
        case 'number':
            return createNumberRow(item, dataPath, isReadonly);
        case 'select':
            return createSelectRow(item, dataPath, isReadonly);
        case 'button':
            return createButtonRow(item, dataPath, isReadonly);
        case 'button_row':
            return createButtonRowGroup(item);
        case 'textarea':
            return createTextareaRow(item, dataPath, isReadonly); // Returns ARRAY
        case 'color':
            return createColorRow(item, dataPath, isReadonly);
        case 'keyvalue':
            return createKeyValueRow(item, dataPath);
        default:
            return createDefaultRow(item);
    }
}

// Toggle switch
function createToggleRow(item, dataPath, isReadonly) {
    const row = document.createElement('div');
    row.className = 'card-row';

    // Label
    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    row.appendChild(label);

    // Toggle widget
    const toggleLabel = document.createElement('label');
    toggleLabel.className = 'toggle';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = item.value === true;
    checkbox.disabled = isReadonly;

    // Only add change listener if not readonly
    if (dataPath && !isReadonly) {
        checkbox.addEventListener('change', (e) => {
            apiSet({ [dataPath]: e.target.checked });
        });
    }

    // Register for updates if needed
    if (item.update && dataPath) {
        registerForUpdates(dataPath, (newValue) => {
            checkbox.checked = newValue === true;
        });
    }

    const slider = document.createElement('span');
    slider.className = 'toggle-slider';

    toggleLabel.appendChild(checkbox);
    toggleLabel.appendChild(slider);
    row.appendChild(toggleLabel);

    return row;
}

// Slider (returns 2 rows)
function createSliderRow(item, dataPath, isReadonly) {
    const rows = [];

    // Row 1: Label + current value
    const labelRow = document.createElement('div');
    labelRow.className = 'card-row slider-row';

    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    labelRow.appendChild(label);

    const valueSpan = document.createElement('span');
    valueSpan.className = 'row-value';
    valueSpan.textContent = item.value + (item.unit || '');
    labelRow.appendChild(valueSpan);

    rows.push(labelRow);

    // Row 2: Slider input
    const sliderRow = document.createElement('div');
    sliderRow.className = 'card-row';

    const slider = document.createElement('input');
    slider.type = 'range';
    slider.className = 'slider';
    slider.min = item.min || 0;
    slider.max = item.max || 100;
    slider.step = item.step || 1;
    slider.value = item.value;
    slider.disabled = isReadonly;

    slider.addEventListener('input', (e) => {
        valueSpan.textContent = e.target.value + (item.unit || '');
    });

    // Only add change listener if not readonly
    if (dataPath && !isReadonly) {
        slider.addEventListener('change', (e) => {
            apiSet({ [dataPath]: parseFloat(e.target.value) });
        });
    }

    // Register for updates if needed
    if (item.update && dataPath) {
        registerForUpdates(dataPath, (newValue) => {
            slider.value = newValue;
            valueSpan.textContent = newValue + (item.unit || '');
        });
    }

    sliderRow.appendChild(slider);
    rows.push(sliderRow);

    return rows;
}

// Number stepper
function createNumberRow(item, dataPath, isReadonly) {
    const row = document.createElement('div');
    row.className = 'card-row';

    // Label
    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    row.appendChild(label);

    // Number stepper
    const stepper = document.createElement('div');
    stepper.className = 'number-stepper';

    // Minus button
    const minusBtn = document.createElement('button');
    minusBtn.className = 'stepper-btn';
    minusBtn.innerHTML = `<svg viewBox="0 0 24 24"><path fill="currentColor" d="M19,13H5V11H19V13Z" /></svg>`;
    minusBtn.disabled = isReadonly;

    // Input
    const input = document.createElement('input');
    input.type = 'number';
    input.className = 'stepper-input';
    input.value = item.value;
    if (item.min !== undefined) input.min = item.min;
    if (item.max !== undefined) input.max = item.max;
    input.step = item.step || 1;
    input.disabled = isReadonly;

    // Plus button
    const plusBtn = document.createElement('button');
    plusBtn.className = 'stepper-btn';
    plusBtn.innerHTML = `<svg viewBox="0 0 24 24"><path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" /></svg>`;
    plusBtn.disabled = isReadonly;

    // Event handlers - only if not readonly
    if (dataPath && !isReadonly) {
        minusBtn.addEventListener('click', () => {
            input.stepDown();
            apiSet({ [dataPath]: parseFloat(input.value) });
        });

        plusBtn.addEventListener('click', () => {
            input.stepUp();
            apiSet({ [dataPath]: parseFloat(input.value) });
        });

        input.addEventListener('change', (e) => {
            apiSet({ [dataPath]: parseFloat(e.target.value) });
        });
    }

    // Register for updates if needed
    if (item.update && dataPath) {
        registerForUpdates(dataPath, (newValue) => {
            input.value = newValue;
        });
    }

    stepper.appendChild(minusBtn);
    stepper.appendChild(input);
    stepper.appendChild(plusBtn);
    row.appendChild(stepper);

    return row;
}

// Select dropdown
function createSelectRow(item, dataPath, isReadonly) {
    const row = document.createElement('div');
    row.className = 'card-row';

    // Label
    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    row.appendChild(label);

    // Select
    const select = document.createElement('select');
    select.className = 'inline-select';
    select.disabled = isReadonly;

    const options = item.choices;
    if (options) {
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option;
            opt.textContent = option;
            if (option === item.value) opt.selected = true;
            select.appendChild(opt);
        });
    }

    // Only add change listener if not readonly
    if (dataPath && !isReadonly) {
        select.addEventListener('change', (e) => {
            apiSet({ [dataPath]: e.target.value });
        });
    }

    // Register for updates if needed
    if (item.update && dataPath) {
        registerForUpdates(dataPath, (newValue) => {
            select.value = newValue;
        });
    }

    row.appendChild(select);
    return row;
}

// Button
function createButtonRow(item, dataPath, isReadonly) {
    const row = document.createElement('div');
    row.className = 'card-row';

    const button = document.createElement('button');
    button.className = 'btn btn-primary';
    button.textContent = item.value || item.label;
    button.disabled = isReadonly;

    // Only add click listener if not readonly
    if (dataPath && !isReadonly) {
        button.addEventListener('click', () => {
            apiSet({ [dataPath]: {} });
        });
    }

    row.appendChild(button);
    return row;
}

// Textarea (returns 2 rows)
function createTextareaRow(item, dataPath, isReadonly) {
    const rows = [];

    // Row 1: Label
    const labelRow = document.createElement('div');
    labelRow.className = 'card-row';

    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    labelRow.appendChild(label);
    rows.push(labelRow);

    // Row 2: Textarea
    const textareaRow = document.createElement('div');
    textareaRow.className = 'card-row';

    const textarea = document.createElement('textarea');
    textarea.className = 'form-textarea';
    textarea.rows = item.lines || 4;
    textarea.value = item.value || '';
    textarea.disabled = isReadonly;

    // Only add change listener if not readonly
    if (dataPath && !isReadonly) {
        textarea.addEventListener('change', (e) => {
            apiSet({ [dataPath]: e.target.value });
        });
    }

    // Register for updates if needed
    if (item.update && dataPath) {
        registerForUpdates(dataPath, (newValue) => {
            textarea.value = newValue;
        });
    }

    textareaRow.appendChild(textarea);
    rows.push(textareaRow);

    return rows;
}

// Text input (readable + writable)
function createInputRow(item, dataPath, isReadonly) {
    const row = document.createElement('div');
    row.className = 'card-row';

    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    row.appendChild(label);

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'inline-input';
    input.value = item.value || '';
    input.disabled = isReadonly;

    if (dataPath && !isReadonly) {
        input.addEventListener('change', (e) => {
            apiSet({ [dataPath]: e.target.value });
        });
    }

    if (item.update && dataPath) {
        registerForUpdates(dataPath, (newValue) => {
            input.value = newValue;
        });
    }

    row.appendChild(input);
    return row;
}

// Password (write-only, masked input)
function createPasswordRow(item, dataPath, isReadonly) {
    const row = document.createElement('div');
    row.className = 'card-row';

    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    row.appendChild(label);

    const input = document.createElement('input');
    input.type = 'password';
    input.className = 'password-input';
    input.placeholder = '***';
    input.disabled = isReadonly;

    if (dataPath && !isReadonly) {
        input.addEventListener('change', (e) => {
            if (e.target.value) {
                apiSet({ [dataPath]: e.target.value });
                e.target.value = '';
            }
        });
    }

    row.appendChild(input);
    return row;
}

// Text (same as no-widget default: label + value)
function createTextRow(item, dataPath) {
    const row = document.createElement('div');
    row.className = 'card-row';

    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    row.appendChild(label);

    if (item.value !== undefined) {
        const value = document.createElement('span');
        value.className = 'row-value';
        value.textContent = item.value + (item.unit || '');
        row.appendChild(value);

        if (item.update && dataPath) {
            registerForUpdates(dataPath, (newValue) => {
                value.textContent = newValue + (item.unit || '');
            });
        }
    }

    return row;
}

// Button row group: multiple buttons in one row
function createButtonRowGroup(item) {
    const row = document.createElement('div');
    row.className = 'card-row';

    // Shared label on the left
    const label = document.createElement('span');
    label.className = 'row-label';
    label.textContent = item.label;
    row.appendChild(label);

    // Button container on the right
    const btnGroup = document.createElement('div');
    btnGroup.className = 'button-row-group';

    for (const btn of item.buttons) {
        const button = document.createElement('button');
        button.className = 'btn btn-row';
        const isReadonly = !btn.write;
        button.disabled = isReadonly;

        if (btn.icon) {
            button.innerHTML = createIcon(btn.icon, 'btn-icon');
        } else {
            button.textContent = btn.value || btn.label;
        }

        if (btn.dataPath && !isReadonly) {
            button.addEventListener('click', () => {
                apiSet({ [btn.dataPath]: {} });
            });
        }

        btnGroup.appendChild(button);
    }

    row.appendChild(btnGroup);
    return row;
}

// Color swatch that opens the color picker modal
function createColorRow(item, dataPath, isReadonly) {
    const row = document.createElement('div');
    row.className = 'card-row';

    const label = document.createElement('span');
    label.className = 'row-label';
    if (item.icon) {
        label.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        label.textContent = item.label;
    }
    row.appendChild(label);

    // Color swatch preview
    const swatch = document.createElement('div');
    swatch.className = 'color-swatch';
    swatch.style.backgroundColor = rgbToHex(item.value);

    if (!isReadonly && dataPath) {
        swatch.addEventListener('click', () => {
            openColorPicker(item.value, dataPath, swatch);
        });
    }

    if (item.update && dataPath) {
        registerForUpdates(dataPath, (newValue) => {
            swatch.style.backgroundColor = rgbToHex(newValue);
            item.value = newValue;
        });
    }

    row.appendChild(swatch);
    return row;
}

// Convert [r, g, b] (0-255) to '#rrggbb'
function rgbToHex(rgb) {
    if (!Array.isArray(rgb) || rgb.length < 3) return '#000000';
    const r = Math.round(rgb[0]);
    const g = Math.round(rgb[1]);
    const b = Math.round(rgb[2]);
    return '#' + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
}

// Convert '#rrggbb' to [r, g, b]
function hexToRgb(hex) {
    const n = parseInt(hex.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

// Open the color picker modal
function openColorPicker(currentValue, dataPath, swatch) {
    const modal = document.getElementById('color-picker-modal');
    const colorInput = document.getElementById('color-input');
    const preview = document.getElementById('color-preview-large');
    const applyBtn = document.getElementById('apply-color');
    const cancelBtn = document.getElementById('cancel-color');
    const closeBtn = document.getElementById('close-color-picker');
    const overlay = document.getElementById('modal-overlay');

    const hex = rgbToHex(currentValue);
    colorInput.value = hex;
    preview.style.backgroundColor = hex;

    modal.classList.add('active');

    colorInput.oninput = () => {
        preview.style.backgroundColor = colorInput.value;
    };

    // Preset color buttons
    const presets = modal.querySelectorAll('.preset-color');
    presets.forEach(btn => {
        btn.onclick = () => {
            colorInput.value = btn.dataset.color;
            preview.style.backgroundColor = btn.dataset.color;
        };
    });

    function closeModal() {
        modal.classList.remove('active');
        applyBtn.onclick = null;
        cancelBtn.onclick = null;
        closeBtn.onclick = null;
        overlay.onclick = null;
    }

    applyBtn.onclick = () => {
        const rgb = hexToRgb(colorInput.value);
        swatch.style.backgroundColor = colorInput.value;
        apiSet({ [dataPath]: rgb });
        closeModal();
    };

    cancelBtn.onclick = closeModal;
    closeBtn.onclick = closeModal;
    overlay.onclick = closeModal;
}

// Key-value list (returns 2 rows: label + inset table)
function createKeyValueRow(item, dataPath) {
    // Single row: inset table with label as header row
    const tableRow = document.createElement('div');
    tableRow.className = 'card-row';

    const table = document.createElement('div');
    table.className = 'kv-table';

    // Header row with label
    const headerRow = document.createElement('div');
    headerRow.className = 'kv-row kv-header';

    const headerLabel = document.createElement('span');
    headerLabel.className = 'kv-key';
    if (item.icon) {
        headerLabel.innerHTML = createIcon(item.icon, 'row-icon') + item.label;
    } else {
        headerLabel.textContent = item.label;
    }
    headerRow.appendChild(headerLabel);
    table.appendChild(headerRow);

    const entries = Array.isArray(item.value) ? item.value : [];
    for (const [key, val] of entries) {
        const kvRow = document.createElement('div');
        kvRow.className = 'kv-row';

        const keySpan = document.createElement('span');
        keySpan.className = 'kv-key';
        keySpan.textContent = key;

        const valSpan = document.createElement('span');
        valSpan.className = 'kv-value';
        valSpan.textContent = String(val) + (item.unit || '');

        kvRow.appendChild(keySpan);
        kvRow.appendChild(valSpan);
        table.appendChild(kvRow);
    }

    if (item.update && dataPath) {
        registerForUpdates(dataPath, (newValue) => {
            // Remove all rows except the header
            while (table.children.length > 1) {
                table.removeChild(table.lastChild);
            }
            const updated = Array.isArray(newValue) ? newValue : [];
            for (const [key, val] of updated) {
                const kvRow = document.createElement('div');
                kvRow.className = 'kv-row';

                const keySpan = document.createElement('span');
                keySpan.className = 'kv-key';
                keySpan.textContent = key;

                const valSpan = document.createElement('span');
                valSpan.className = 'kv-value';
                valSpan.textContent = String(val) + (item.unit || '');

                kvRow.appendChild(keySpan);
                kvRow.appendChild(valSpan);
                table.appendChild(kvRow);
            }
        });
    }

    tableRow.appendChild(table);
    return tableRow;
}

function createDefaultRow(item) {
    const row = document.createElement('div');
    row.className = 'card-row';
    row.textContent = `Unknown widget: ${item.widget}`;
    return row;
}