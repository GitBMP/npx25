
// Label toggle functionality
const btnLabel = document.getElementById('btn-label');
const iconUse = btnLabel.querySelector('use');
let labelsVisible = false;

btnLabel.addEventListener('click', () => {
    labelsVisible = !labelsVisible;

    // Toggle icon
    if (labelsVisible) {
        iconUse.setAttribute('href', '#icon-label');
    } else {
        iconUse.setAttribute('href', '#icon-label-off');
    }

    // Toggle visibility of all card footers
    const footers = document.querySelectorAll('.card-footer');
    footers.forEach(footer => {
        footer.style.display = labelsVisible ? 'flex' : 'none';
    });
});


// Edit mode toggle
const btnEdit = document.getElementById('btn-edit');
const editIconUse = btnEdit.querySelector('use');
let editMode = false;

btnEdit.addEventListener('click', () => {
    // Disable edit for utility views
    const activeNav = document.querySelector('.nav-item.active');
    if (activeNav && activeNav.dataset.view === 'utility') return;

    // Exiting edit mode: collect state before toggling
    if (editMode) {
        collectEditState();
    }

    editMode = !editMode;
    editIconUse.setAttribute('href', editMode ? '#icon-pencil' : '#icon-pencil-off');
    document.body.classList.toggle('edit-mode', editMode);

    // Re-render current cards
    if (activeNav && activeNav.dataset.path !== undefined) {
        loadCards({ path: activeNav.dataset.path });
    }
});


// Sync toggle functionality
const btnSync = document.getElementById('btn-sync');
const syncIconUse = btnSync.querySelector('use');

// Update the sync icon based on update interval state
function updateSyncIcon() {
    if (updateInterval !== null) {
        syncIconUse.setAttribute('href', '#icon-sync');
    } else {
        syncIconUse.setAttribute('href', '#icon-sync-off');
    }
}

// Toggle updates on/off when clicking sync button
btnSync.addEventListener('click', () => {
    if (updateInterval !== null) {
        stopUpdateInterval();
    } else {
        startUpdateInterval();
    }
    updateSyncIcon();
});