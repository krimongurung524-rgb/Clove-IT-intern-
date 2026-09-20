/**
 * Search page interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-submit filters on change (optional)
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        // Sort change
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                const url = new URL(window.location);
                url.searchParams.set('sort', this.value);
                window.location = url;
            });
        }
    }

    // Price range validation
    const minPrice = document.querySelector('input[name="min_price"]');
    const maxPrice = document.querySelector('input[name="max_price"]');
    
    if (minPrice && maxPrice) {
        maxPrice.addEventListener('change', function() {
            if (minPrice.value && parseFloat(this.value) < parseFloat(minPrice.value)) {
                alert('Max price should be greater than min price');
                this.value = '';
            }
        });
    }
});
