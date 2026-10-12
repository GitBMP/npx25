// Sequential script loader for MicroPython
const scriptsToLoad = [
    '/utils.js',
    '/api.js',
    '/update.js',
    '/cardItem.js',
    '/cards.js',
    '/topbar.js',
    '/sidebar.js',
    '/index.js'  // IIFE - load last
];

let loadIndex = 0;

function loadNextScript() {
    if (loadIndex >= scriptsToLoad.length) {
        console.log('All scripts loaded');
        // Trigger init here if needed
        if (typeof init === 'function') init();
        return;
    }

    const script = document.createElement('script');
    script.src = scriptsToLoad[loadIndex];
    script.onload = () => {
        console.log('Loaded: ' + scriptsToLoad[loadIndex]);
        loadIndex++;
        loadNextScript();
    };
    script.onerror = () => {
        console.error('Failed to load: ' + scriptsToLoad[loadIndex]);
        loadIndex++;
        loadNextScript();
    };

    document.head.appendChild(script);
}

// Start loading
loadNextScript();
