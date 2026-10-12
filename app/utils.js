
function createIcon(iconId, className = '') {
    // If no 'icon-' prefix, add it
    if (!iconId.startsWith('icon-')) {
        iconId = 'icon-' + iconId;
    }
    const svg = `<svg class="${className}" viewBox="0 0 24 24"><use href="#${iconId}"></use></svg>`;
    return svg;
}

// Load SVG icons into the DOM
async function loadIcons() {
    try {
        const response = await fetch('/icons.svg');
        if (!response.ok) {
            throw new Error(`Failed to load icons: ${response.status}`);
        }
        const svgText = await response.text();

        // Remove existing icon container if present
        const existingContainer = document.getElementById('svg-icon-container');
        if (existingContainer) {
            existingContainer.remove();
        }

        // Create a container div and inject the SVG
        const container = document.createElement('div');
        container.id = 'svg-icon-container';
        container.style.display = 'none';
        container.innerHTML = svgText;
        document.body.insertBefore(container, document.body.firstChild);

        console.log('Icons loaded successfully');
    } catch (error) {
        console.error('Error loading icons:', error);
    }
}