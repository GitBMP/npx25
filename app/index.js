

// IIFE
(async () => {
    console.log('IIFE starting up ...');

    await loadIcons();
    console.log('Icons loaded');

    await loadSidebar();
    console.log('Sidebar loaded');
})();

