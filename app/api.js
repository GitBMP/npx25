async function apiGet(paths) {
    try {
        const response = await fetch(`/api/get`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(paths)
        });
        return await response.json();
    } catch (error) {
        console.error('API GET error:', error);
        return null;
    }
}

async function apiSet(pathValuePairs) {
    try {
        const response = await fetch(`/api/set`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pathValuePairs)
        });
        return response.ok;
    } catch (error) {
        console.error('API SET error:', error);
        return false;
    }
}

async function apiGetSidebar() {
    try {
        const response = await fetch(`/api/sidebar`);
        return await response.json();
    } catch (error) {
        console.error('API Sidebar error:', error);
        return null;
    }
}

async function apiGetCards(request) {
    try {
        const response = await fetch(`/api/cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });
        return await response.json();
    } catch (error) {
        console.error('API Cards error:', error);
        return null;
    }
}