/**
 * Dashboard interactions
 */
document.addEventListener('DOMContentLoaded', function() {
    // Highlight active sidebar link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.dashboard-sidebar .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
