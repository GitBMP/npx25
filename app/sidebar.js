const favNav = document.getElementById('sidebar-nav-favourites');
const containerNav = document.getElementById('sidebar-nav-container');
const bottomNav = document.getElementById('sidebar-nav-bottom');

// Available favourites for "Add to" in edit mode
let favouritesList = [];

const navTargets = {
    favourite: favNav,
    container: containerNav,
    utility: bottomNav,
};

async function loadSidebar() {
    const sidebarData = await apiGetSidebar();
    if (!sidebarData) return;

    for (let entry of sidebarData) {
        const target = navTargets[entry.view];
        if (target) createNavItem(entry, target);
    }

    // Store favourites for "Add to" dropdown
    favouritesList = sidebarData
        .filter(e => e.view === 'favourite')
        .map(e => ({ path: e.path, name: e.name || e.path.split('.').pop() }));

    // Load initial cards - first favourite or DC root
    const firstFav = sidebarData.find(e => e.view === 'favourite');
    const initialPath = firstFav ? firstFav.path : '';
    const initialNav = document.querySelector(`.nav-item[data-path="${initialPath}"]`);
    if (initialNav) initialNav.classList.add('active');
    loadCards({ path: initialPath });
}

function createNavItem(entry, targetNav) {
    const displayName = entry.name || entry.path.split('.').pop() || 'root';

    const item = document.createElement('a');
    item.href = '#';
    item.className = 'nav-item';
    item.dataset.path = entry.path;
    item.dataset.view = entry.view;

    item.innerHTML = `
        ${entry.icon ? createIcon(entry.icon, 'nav-icon') : createIcon('icon-barcode', 'nav-icon')}
        <span class="nav-text">${displayName}</span>
    `;

    item.addEventListener('click', handleNavClick);
    targetNav.appendChild(item);
}

function handleNavClick(e) {
    e.preventDefault();
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    e.currentTarget.classList.add('active');

    // Exit edit mode on navigation
    if (editMode) {
        collectEditState();
        editMode = false;
        editIconUse.setAttribute('href', '#icon-pencil-off');
        document.body.classList.remove('edit-mode');
    }

    loadCards({ path: e.currentTarget.dataset.path });
}
