// Auto-update system for card items
// Batches all update requests into a single API call every 2 seconds

const updateRegistry = new Map(); // path -> array of updateCallbacks
let updateInterval = null;
let updateInProgress = false;
const UPDATE_INTERVAL_MS = 1000;

/**
 * Register an item for auto-updates
 * @param {string} path - The data path to fetch (e.g., "poti_raw.pin")
 * @param {function} updateCallback - Function to call with new value: (newValue) => void
 */
function registerForUpdates(path, updateCallback) {
    if (!path || !updateCallback) return;

    // Get existing callbacks array or create new one
    if (!updateRegistry.has(path)) {
        updateRegistry.set(path, []);
    }

    // Add callback to the array
    updateRegistry.get(path).push(updateCallback);

    // Start interval if this is the first registration
    if (updateRegistry.size === 1) {
        startUpdateInterval();
    }
}

/**
 * Unregister an item from auto-updates
 * @param {string} path - The data path to stop updating
 * @param {function} updateCallback - The specific callback to remove (optional - if not provided, removes all)
 */
function unregisterForUpdates(path, updateCallback) {
    if (!updateRegistry.has(path)) return;

    if (updateCallback) {
        // Remove specific callback
        const callbacks = updateRegistry.get(path);
        const index = callbacks.indexOf(updateCallback);
        if (index > -1) {
            callbacks.splice(index, 1);
        }

        // If no callbacks left for this path, remove the path entirely
        if (callbacks.length === 0) {
            updateRegistry.delete(path);
        }
    } else {
        // Remove all callbacks for this path
        updateRegistry.delete(path);
    }

    // Stop interval if no more items to update
    if (updateRegistry.size === 0) {
        stopUpdateInterval();
    }
}

/**
 * Clear all registrations (call when loading new cards)
 */
function clearUpdateRegistry() {
    updateRegistry.clear();
    stopUpdateInterval();
}

/**
 * Batch update all registered items
 * Fetches all paths in a single API call and updates UI
 */
async function batchUpdate() {
    if (updateRegistry.size === 0) return;
    if (updateInProgress) return;

    updateInProgress = true;

    try {
        const paths = Array.from(updateRegistry.keys());
        const values = await apiGet(paths);

        if (!values) return;

        for (const [path, callbacks] of updateRegistry.entries()) {
            if (values[path] !== undefined) {
                callbacks.forEach(callback => callback(values[path]));
            }
        }
    } finally {
        updateInProgress = false;
    }
}

/**
 * Start the update interval
 */
function startUpdateInterval() {
    if (updateInterval) return; // Already running

    console.log('Starting update interval...');
    updateInterval = setInterval(batchUpdate, UPDATE_INTERVAL_MS);
    if (typeof updateSyncIcon === 'function') updateSyncIcon();
}

/**
 * Stop the update interval
 */
function stopUpdateInterval() {
    if (updateInterval) {
        console.log('Stopping update interval...');
        clearInterval(updateInterval);
        updateInterval = null;
        if (typeof updateSyncIcon === 'function') updateSyncIcon();
    }
}

/**
 * Get current registry stats (for debugging)
 */
function getUpdateStats() {
    const totalCallbacks = Array.from(updateRegistry.values()).reduce((sum, callbacks) => sum + callbacks.length, 0);
    return {
        registeredPaths: updateRegistry.size,
        totalCallbacks: totalCallbacks,
        paths: Array.from(updateRegistry.keys()),
        intervalActive: updateInterval !== null
    };
}
