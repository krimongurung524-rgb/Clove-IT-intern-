/**
 * Favorites toggle functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const propertyId = this.dataset.propertyId;
            const icon = this.querySelector('i');
            const isFavorited = this.dataset.isFavorited === 'true';
            
            fetch(`/favorites/toggle/${propertyId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.dataset.isFavorited = data.is_favorited;
                    if (data.is_favorited) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                    }
                    
                    // Show toast notification
                    showToast(data.message, 'success');
                }
            })
            .catch(err => {
                console.error('Favorite toggle error:', err);
                showToast('Please login to save favorites', 'warning');
            });
        });
    });
});

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = 'top: 90px; right: 20px; z-index: 9999; min-width: 250px;';
    toast.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
