from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from properties.models import Property
from .models import Favorite


@login_required
def toggle_favorite(request, property_id):
    """Add or remove from favorites (AJAX or normal)"""
    property_obj = get_object_or_404(Property, pk=property_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        property=property_obj
    )
    
    if not created:
        favorite.delete()
        is_favorited = False
        message = 'Removed from favorites'
    else:
        is_favorited = True
        message = 'Added to favorites'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message
        })
    
    messages.success(request, message)
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or 'properties:search'
    return redirect(next_url)


@login_required
def saved_rooms(request):
    """List user's favorite properties"""
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'property', 'property__owner'
    ).prefetch_related('property__images')
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'dashboard/saved_rooms.html', context)
