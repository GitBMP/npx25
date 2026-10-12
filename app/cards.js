// Local overrides for favourite attrs (keyed by card path)
const editOverrides = {};

// Favourite card definitions override (keyed by favourite path)
const favouriteCardOverrides = {};

function removeCardFromFavourite(cardPath) {
    const activeNav = document.querySelector('.nav-item.active');
    const favPath = activeNav?.dataset.path;
    if (!favPath) return;

    if (favouriteCardOverrides[favPath]) {
        favouriteCardOverrides[favPath] = favouriteCardOverrides[favPath].filter(c => c.path !== cardPath);
    }
    // Also remove attr overrides for this card
    delete editOverrides[cardPath];
    console.log(`Removed ${cardPath} from ${favPath}`);
}

function addCardToFavourite(cardPath, favPath) {
    if (!favouriteCardOverrides[favPath]) {
        favouriteCardOverrides[favPath] = [];
    }
    // Don't add duplicates
    if (favouriteCardOverrides[favPath].some(c => c.path === cardPath)) {
        console.log(`${cardPath} already in ${favPath}`);
        return;
    }
    favouriteCardOverrides[favPath].push({ path: cardPath });
    console.log(`Added ${cardPath} to ${favPath}:`, favouriteCardOverrides[favPath]);
    apiSet({ [favPath + '.add_card']: cardPath });
}

function collectEditState() {
    const activeNav = document.querySelector('.nav-item.active');
    const activeView = activeNav?.dataset.view;
    const activePath = activeNav?.dataset.path;

    const cards = document.querySelectorAll('.card');

    // For favourites, track which cards survive
    if (activeView === 'favourite' && activePath) {
        const survivingCards = [];
        for (const card of cards) {
            if (card.dataset.path) survivingCards.push(card.dataset.path);
        }
        favouriteCardOverrides[activePath] = survivingCards.map(p => ({ path: p }));
        console.log(`Cards saved for ${activePath}:`, survivingCards);
    }

    for (const card of cards) {
        const cardPath = card.dataset.path;
        if (!cardPath) continue;

        const rows = card.querySelectorAll('.edit-row:not(.edit-ghost-separator)');
        if (rows.length === 0) continue;

        const attrs = [];
        for (const row of rows) {
            const key = row.dataset.key;
            if (key === '---') {
                attrs.push('---');
            } else {
                const checkbox = row.querySelector('.edit-checkbox');
                if (checkbox && checkbox.checked) {
                    if (row.dataset.keys) {
                        for (const k of row.dataset.keys.split(',')) attrs.push(k);
                    } else {
                        attrs.push(key);
                    }
                }
            }
        }
        editOverrides[cardPath] = attrs;
        console.log(`Edit saved for ${cardPath}:`, attrs);
    }

    // Writeback favourites to server
    if (activeView === 'favourite' && activePath) {
        saveFavourite(activePath);
    }
}

function saveFavourite(favPath) {
    const cardOverrides = favouriteCardOverrides[favPath];
    if (!cardOverrides) return;

    const cards = cardOverrides.map(c => {
        const entry = { path: c.path };
        const attrs = editOverrides[c.path];
        if (attrs && attrs.length > 0) {
            entry.attrs = attrs;
        }
        return entry;
    });

    console.log(`Saving favourite ${favPath}:`, cards);
    apiSet({ [favPath + '.cards']: cards });
}

async function loadCards(request) {
    console.log('Loading Cards')
    console.log(request);

    clearUpdateRegistry();

    let cards = await apiGetCards(request);
    if(!cards) return;

    // Filter cards by favouriteCardOverrides if available
    const activeNav = document.querySelector('.nav-item.active');
    const activePath = activeNav?.dataset.path;
    if (activePath && favouriteCardOverrides[activePath]) {
        const allowedPaths = favouriteCardOverrides[activePath].map(c => c.path);
        cards = cards.filter(c => allowedPaths.includes(c.path));
    }

    console.log(cards);

    const container = document.getElementById('cards-container');
    container.innerHTML = '';

    for (let cardData of cards) {
        const cardElement = createCard(cardData);
        container.appendChild(cardElement);
    }
}

function createCard(cardData) {
    const card = document.createElement('div');
    card.className = 'card';
    if (cardData.path) card.dataset.path = cardData.path;

    // Card content wrapper
    const content = document.createElement('div');
    content.className = 'card-content';

    // Build items from flat attributes
    const items = [];

    // Heading: use last segment of path as name
    const name = cardData.path ? cardData.path.split('.').pop() : cardData.class;
    items.push({ label: name, icon: cardData.icon });

    // Determine which attrs to show
    const isFavourite = !!cardData.favourite;
    const allKeys = Object.keys(cardData).filter(k => k !== 'class' && k !== 'path' && k !== 'icon' && k !== 'favourite');

    // Apply local overrides if available
    if (isFavourite && editOverrides[cardData.path]) {
        cardData.favourite.attrs = editOverrides[cardData.path];
    }
    const checkedKeys = isFavourite ? cardData.favourite.attrs.filter(a => a !== '---') : [];

    // Determine attr order
    let attrKeys;
    if (isFavourite && editMode) {
        // Whitelisted items in order first (including ---), then remaining unchecked
        const favAttrs = cardData.favourite.attrs;
        const remaining = allKeys.filter(k => !checkedKeys.includes(k));
        attrKeys = [...favAttrs, ...remaining];
    } else if (isFavourite) {
        attrKeys = cardData.favourite.attrs;
    } else {
        attrKeys = allKeys;
    }

    // Convert each attribute to a card item
    for (const key of attrKeys) {
        if (key === '---') {
            items.push({ widget: 'separator', key: '---', checked: true });
            continue;
        }
        const attr = cardData[key];
        if (!attr) continue;

        const item = {
            key: key,
            label: attr.label || key,
            value: attr.value,
            widget: attr.widget,
            dataPath: cardData.path ? cardData.path + '.' + key : key,
            read: attr.read,
            write: attr.write,
            type: attr.type,
            min: attr.min,
            max: attr.max,
            step: attr.step,
            choices: attr.choices,
            icon: attr.icon,
            update: attr.update,
            unit: attr.unit,
            lines: attr.lines,
            group: attr.group,
            checked: isFavourite ? checkedKeys.includes(key) : false
        };
        items.push(item);
    }

    // Group button_row items by group
    const grouped = [];
    const seenGroups = new Set();
    for (const item of items) {
        if (item.widget === 'button_row' && item.group) {
            if (seenGroups.has(item.group)) continue;
            seenGroups.add(item.group);
            const buttons = items.filter(i => i.widget === 'button_row' && i.group === item.group);
            grouped.push({
                widget: 'button_row',
                key: item.group,
                label: item.label,
                buttons: buttons,
                checked: buttons.some(b => b.checked)
            });
        } else {
            grouped.push(item);
        }
    }

    // Render all items
    for (let i = 0; i < grouped.length; i++) {
        const itemElements = createCardItem(grouped[i]);

        // First item is the heading - add special class
        if (i === 0) {
            if (Array.isArray(itemElements)) {
                itemElements[0].classList.add('card-heading');
            } else {
                itemElements.classList.add('card-heading');
            }
            // Heading is never wrapped in edit mode
            const headingEl = Array.isArray(itemElements) ? itemElements[0] : itemElements;

            // Add trash icon for favourite cards in edit mode
            if (editMode && isFavourite) {
                const trashBtn = document.createElement('button');
                trashBtn.className = 'edit-trash-btn';
                trashBtn.innerHTML = `<svg viewBox="0 0 24 24"><use href="#icon-trash-can-outline"></use></svg>`;
                trashBtn.addEventListener('click', () => {
                    removeCardFromFavourite(cardData.path);
                    card.remove();
                });
                headingEl.appendChild(trashBtn);
            }

            if (Array.isArray(itemElements)) {
                itemElements.forEach(el => content.appendChild(el));
            } else {
                content.appendChild(itemElements);
            }
            continue;
        }

        // In edit mode for favourites, wrap each item with checkbox + drag handle
        if (editMode && isFavourite) {
            const wrapper = createEditWrapper(grouped[i], itemElements);
            content.appendChild(wrapper);
        } else {
            if (Array.isArray(itemElements)) {
                itemElements.forEach(el => content.appendChild(el));
            } else {
                content.appendChild(itemElements);
            }
        }
    }

    // In edit mode, add static ghost separator at the bottom (spawner)
    if (editMode && isFavourite) {
        const ghost = createSeparatorRow();
        ghost.classList.add('edit-ghost-separator');
        content.appendChild(ghost);
    }

    // In edit mode for containers, add "Add to favourite" dropdown
    const activeView = document.querySelector('.nav-item.active')?.dataset.view;
    if (editMode && activeView === 'container' && favouritesList.length > 0) {
        const addRow = document.createElement('div');
        addRow.className = 'card-row edit-add-row';

        const label = document.createElement('span');
        label.className = 'row-label';
        label.textContent = 'Add to';
        addRow.appendChild(label);

        const select = document.createElement('select');
        select.className = 'inline-select';

        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = 'Select...';
        placeholder.disabled = true;
        placeholder.selected = true;
        select.appendChild(placeholder);

        for (const fav of favouritesList) {
            const opt = document.createElement('option');
            opt.value = fav.path;
            opt.textContent = fav.name;
            select.appendChild(opt);
        }

        select.addEventListener('change', () => {
            if (!select.value) return;
            addCardToFavourite(cardData.path, select.value);
            select.selectedIndex = 0;
        });

        addRow.appendChild(select);
        content.appendChild(addRow);
    }

    card.appendChild(content);

    // Add footer with class and path info
    if (cardData.class || cardData.path) {
        const footer = document.createElement('div');
        footer.className = 'card-footer';

        const classSpan = document.createElement('span');
        classSpan.className = 'card-class';
        classSpan.textContent = cardData.class || '';
        footer.appendChild(classSpan);

        const pathSpan = document.createElement('span');
        pathSpan.className = 'card-path';
        pathSpan.textContent = cardData.path || '';
        footer.appendChild(pathSpan);

        card.appendChild(footer);
    }

    return card;
}


function createEditWrapper(item, itemElements) {
    // Separators get their own row type
    if (item.widget === 'separator') {
        return createSeparatorRow();
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'edit-row';
    wrapper.dataset.key = item.key || '';

    // For grouped button rows, store individual keys for expand on collect
    if (item.buttons) {
        wrapper.dataset.keys = item.buttons.map(b => b.key).join(',');
    }

    // Checkbox
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'edit-checkbox';
    checkbox.checked = item.checked === true;
    wrapper.appendChild(checkbox);

    // Content
    const contentWrap = document.createElement('div');
    contentWrap.className = 'edit-row-content';
    if (Array.isArray(itemElements)) {
        itemElements.forEach(el => contentWrap.appendChild(el));
    } else {
        contentWrap.appendChild(itemElements);
    }
    wrapper.appendChild(contentWrap);

    // Drag handle
    const handle = document.createElement('div');
    handle.className = 'edit-drag-handle';
    handle.innerHTML = `<svg viewBox="0 0 24 24"><use href="#icon-menu"></use></svg>`;
    wrapper.appendChild(handle);

    addDragBehavior(wrapper);
    return wrapper;
}


function createSeparatorRow() {
    const wrapper = document.createElement('div');
    wrapper.className = 'edit-row edit-separator-row';
    wrapper.dataset.key = '---';

    // No checkbox, just the hr and drag handle
    const contentWrap = document.createElement('div');
    contentWrap.className = 'edit-row-content';
    contentWrap.appendChild(createCardItem({ widget: 'separator' }));
    wrapper.appendChild(contentWrap);

    const handle = document.createElement('div');
    handle.className = 'edit-drag-handle';
    handle.innerHTML = `<svg viewBox="0 0 24 24"><use href="#icon-menu"></use></svg>`;
    wrapper.appendChild(handle);

    addDragBehavior(wrapper);
    return wrapper;
}


function addDragBehavior(wrapper) {
    wrapper.draggable = true;

    wrapper.addEventListener('dragstart', (e) => {
        // Ghost becomes a real separator when dragged
        if (wrapper.classList.contains('edit-ghost-separator')) {
            wrapper.classList.remove('edit-ghost-separator');
        }
        wrapper.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    });

    wrapper.addEventListener('dragend', () => {
        wrapper.classList.remove('dragging');
        const parent = wrapper.parentElement;
        if (!parent) return;

        // Ensure there's always a ghost at the bottom
        if (!parent.querySelector('.edit-ghost-separator')) {
            const ghost = createSeparatorRow();
            ghost.classList.add('edit-ghost-separator');
            parent.appendChild(ghost);
        }

        // Delete any non-ghost separator that ended up right before the ghost
        const ghost = parent.querySelector('.edit-ghost-separator');
        if (ghost && ghost.previousElementSibling) {
            const prev = ghost.previousElementSibling;
            if (prev.classList.contains('edit-separator-row') && !prev.classList.contains('edit-ghost-separator')) {
                prev.remove();
            }
        }
    });

    wrapper.addEventListener('dragover', (e) => {
        e.preventDefault();
        const parent = wrapper.parentElement;
        const dragging = parent.querySelector('.dragging');
        if (!dragging || dragging === wrapper) return;

        const rect = wrapper.getBoundingClientRect();
        const mid = rect.top + rect.height / 2;
        if (e.clientY < mid) {
            parent.insertBefore(dragging, wrapper);
        } else {
            parent.insertBefore(dragging, wrapper.nextSibling);
        }
    });
}