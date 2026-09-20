/**
 * Map view with Leaflet
 * Carto tiles — OSM openstreetmap.org often returns 403
 */

function initMap(properties) {
    if (typeof L === 'undefined') {
        console.error('Leaflet not loaded');
        return;
    }

    // Default center: Kathmandu
    const map = L.map('map').setView([27.7172, 85.3240], 12);

    // Carto Voyager (free, works without 403)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    const markers = [];

    (properties || []).forEach(function (prop) {
        if (prop.lat && prop.lng) {
            const marker = L.marker([prop.lat, prop.lng]).addTo(map);
            marker.bindPopup(`
                <div style="min-width:200px">
                    <img src="${prop.image || ''}" style="width:100%;height:100px;object-fit:cover;border-radius:8px;margin-bottom:8px;" onerror="this.style.display='none'">
                    <strong>${prop.title || ''}</strong><br>
                    <span style="color:#4F46E5;font-weight:600">Rs. ${Number(prop.price || 0).toLocaleString()}/mo</span><br>
                    <small>${prop.type || ''} • ${prop.city || ''}</small><br>
                    <a href="${prop.url || '#'}" class="btn btn-sm btn-primary mt-2">View Details</a>
                </div>
            `);
            markers.push(marker);
        }
    });

    if (markers.length > 0) {
        const group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.15));
    }

    return map;
}
