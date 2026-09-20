"""
URL configuration for roomfinder project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from properties.views import (
    home, about, contact, page_not_found,
    owner_dashboard, add_property, my_properties, edit_property
)
from favorites.views import saved_rooms
from bookings.views import my_visits
from messaging.views import conversations_list
from favorites.models import Favorite
from bookings.models import VisitBooking
from messaging.models import Conversation


@login_required
def dashboard(request):
    favorites_count = Favorite.objects.filter(user=request.user).count()
    visits = VisitBooking.objects.filter(user=request.user).order_by('-created_at')[:5]
    conversations = Conversation.objects.filter(participants=request.user)[:5]
    
    context = {
        'favorites_count': favorites_count,
        'recent_visits': visits,
        'conversations': conversations,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def inquiries_view(request):
    from properties.models import Inquiry
    if request.user.role == 'owner':
        inquiries = Inquiry.objects.filter(property__owner=request.user).select_related('user', 'property')
    else:
        inquiries = Inquiry.objects.filter(user=request.user).select_related('property')
    return render(request, 'dashboard/inquiries.html', {'inquiries': inquiries})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('properties/', include(('properties.urls', 'properties'), namespace='properties')),
    path('bookings/', include(('bookings.urls', 'bookings'), namespace='bookings')),
    path('favorites/', include(('favorites.urls', 'favorites'), namespace='favorites')),
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),
    path('messaging/', include(('messaging.urls', 'messaging'), namespace='messaging')),
    
    # Tenant Dashboard
    path('dashboard/', include(([
        path('', dashboard, name='dashboard'),
        path('saved/', saved_rooms, name='saved_rooms'),
        path('visits/', my_visits, name='visits'),
        path('messages/', conversations_list, name='messages'),
        path('inquiries/', inquiries_view, name='inquiries'),
    ], 'dashboard'), namespace='dashboard')),
    
    # Owner Dashboard
    path('owner/', include(([
        path('dashboard/', owner_dashboard, name='dashboard'),
        path('add-property/', add_property, name='add_property'),
        path('properties/', my_properties, name='properties'),
        path('properties/<int:pk>/edit/', edit_property, name='edit_property'),
    ], 'owner'), namespace='owner')),
]

handler404 = 'properties.views.page_not_found'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
