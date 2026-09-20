from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Property, PropertyImage, Inquiry
from .forms import PropertyForm, PropertyImageForm, InquiryForm, PropertySearchForm
from favorites.models import Favorite


def home(request):
    """Homepage with featured properties"""
    featured = Property.objects.filter(status='available', is_featured=True)[:6]
    recent = Property.objects.filter(status='available').order_by('-created_at')[:8]
    popular_cities = Property.objects.filter(status='available').values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    context = {
        'featured_properties': featured,
        'recent_properties': recent,
        'popular_cities': popular_cities,
    }
    return render(request, 'home/home.html', context)


def search(request):
    """Search and filter properties"""
    form = PropertySearchForm(request.GET or None)
    properties = Property.objects.filter(status='available').select_related('owner').prefetch_related('images')
    
    if form.is_valid():
        q = form.cleaned_data.get('q')
        property_type = form.cleaned_data.get('property_type')
        city = form.cleaned_data.get('city')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        bedrooms = form.cleaned_data.get('bedrooms')
        furnishing = form.cleaned_data.get('furnishing')
        gender_preference = form.cleaned_data.get('gender_preference')
        has_wifi = form.cleaned_data.get('has_wifi')
        has_parking = form.cleaned_data.get('has_parking')
        has_kitchen = form.cleaned_data.get('has_kitchen')
        has_ac = form.cleaned_data.get('has_ac')
        
        if q:
            properties = properties.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(address__icontains=q) |
                Q(city__icontains=q) |
                Q(area__icontains=q) |
                Q(landmark__icontains=q)
            )
        if property_type:
            properties = properties.filter(property_type=property_type)
        if city:
            properties = properties.filter(city__icontains=city)
        if min_price:
            properties = properties.filter(price__gte=min_price)
        if max_price:
            properties = properties.filter(price__lte=max_price)
        if bedrooms:
            properties = properties.filter(bedrooms__gte=bedrooms)
        if furnishing:
            properties = properties.filter(furnishing=furnishing)
        if gender_preference:
            properties = properties.filter(gender_preference=gender_preference)
        if has_wifi:
            properties = properties.filter(has_wifi=True)
        if has_parking:
            properties = properties.filter(has_parking=True)
        if has_kitchen:
            properties = properties.filter(has_kitchen=True)
        if has_ac:
            properties = properties.filter(has_ac=True)
    
    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        properties = properties.order_by('price')
    elif sort == 'price_high':
        properties = properties.order_by('-price')
    elif sort == 'popular':
        properties = properties.order_by('-views_count')
    else:
        properties = properties.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(properties, 12)
    page = request.GET.get('page')
    properties_page = paginator.get_page(page)
    
    # User favorites for heart icons
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('property_id', flat=True))
    
    context = {
        'form': form,
        'properties': properties_page,
        'total_count': properties.count(),
        'user_favorites': user_favorites,
        'sort': sort,
    }
    return render(request, 'properties/search.html', context)


def property_details(request, pk):
    property_obj = get_object_or_404(
        Property.objects.select_related('owner').prefetch_related('images', 'reviews'),
        pk=pk
    )
    property_obj.increment_views()

    is_favorited = False
    location_unlocked = property_obj.user_can_see_exact_location(request.user)
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, property=property_obj).exists()

    related = Property.objects.filter(city=property_obj.city, status='available').exclude(pk=pk)[:4]
    inquiry_form = InquiryForm()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'message' in request.POST:
            inquiry_form = InquiryForm(request.POST)
            if inquiry_form.is_valid():
                inquiry = inquiry_form.save(commit=False)
                inquiry.property = property_obj
                inquiry.user = request.user
                inquiry.save()
                messages.success(request, 'Your inquiry has been sent to the owner!')
                return redirect('properties:details', pk=pk)

    return render(request, 'properties/details.html', {
        'property': property_obj,
        'is_favorited': is_favorited,
        'related_properties': related,
        'inquiry_form': inquiry_form,
        'amenities': property_obj.get_amenities_list(),
        'location_unlocked': location_unlocked,
        'unlock_fee': property_obj.location_unlock_fee,
    })


def map_view(request):
    import json
    properties = Property.objects.filter(
        status='available',
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('owner').prefetch_related('images')

    props_data = []
    for p in properties:
        if not p.user_can_see_exact_location(request.user):
            continue
        props_data.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price),
            'lat': float(p.latitude),
            'lng': float(p.longitude),
            'type': p.get_property_type_display(),
            'city': p.city,
            'image': p.main_image,
            'url': p.get_absolute_url(),
        })

    return render(request, 'properties/map.html', {
        'properties': properties,
        'props_json': json.dumps(props_data),
    })


@login_required
def add_property(request):
    """Owner: Add new property"""
    if request.user.role not in ['owner', 'admin']:
        messages.error(request, 'Only property owners can add listings.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        images = request.FILES.getlist('images')
        
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            
            for i, image in enumerate(images):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image,
                    is_primary=(i == 0)
                )
            
            messages.success(request, 'Property listed successfully!')
            return redirect('owner:properties')
    else:
        form = PropertyForm()
    
    return render(request, 'owner/add_property.html', {'form': form})

@login_required
def unlock_location(request, pk):
    from .models import LocationUnlock
    from django.utils import timezone
    import uuid

    property_obj = get_object_or_404(Property, pk=pk)

    if property_obj.owner_id == request.user.id:
        messages.info(request, 'You own this property — location is always visible.')
        return redirect('properties:details', pk=pk)

    existing = LocationUnlock.objects.filter(user=request.user, property=property_obj).first()
    if existing and existing.status == 'paid':
        messages.success(request, 'Location already unlocked.')
        return redirect('properties:details', pk=pk)

    if request.method == 'POST':
        amount = property_obj.location_unlock_fee
        LocationUnlock.objects.update_or_create(
            user=request.user,
            property=property_obj,
            defaults={
                'amount': amount,
                'status': 'paid',
                'payment_method': request.POST.get('payment_method', 'demo'),
                'transaction_id': f'DEMO-{uuid.uuid4().hex[:12].upper()}',
                'paid_at': timezone.now(),
            },
        )
        messages.success(request, f'Payment successful (Rs. {amount}). Exact location is now visible.')
        return redirect('properties:details', pk=pk)

    return render(request, 'properties/unlock_location.html', {
        'property': property_obj,
        'unlock_fee': property_obj.location_unlock_fee,
        'existing': existing,
    })


@login_required
def edit_property(request, pk):
    """Owner: Edit property"""
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_obj)
        images = request.FILES.getlist('images')
        
        if form.is_valid():
            form.save()
            
            for i, image in enumerate(images):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image,
                    is_primary=False
                )
            
            messages.success(request, 'Property updated successfully!')
            return redirect('owner:properties')
    else:
        form = PropertyForm(instance=property_obj)
    
    context = {
        'form': form,
        'property': property_obj,
    }
    return render(request, 'owner/edit_property.html', context)


@login_required
def delete_property(request, pk):
    """Owner: Delete property"""
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('owner:properties')
    
    return render(request, 'owner/edit_property.html', {'property': property_obj, 'delete_confirm': True})


@login_required
def my_properties(request):
    """Owner: List own properties"""
    properties = Property.objects.filter(owner=request.user).prefetch_related('images')
    
    context = {
        'properties': properties,
    }
    return render(request, 'owner/properties.html', context)


@login_required
def owner_dashboard(request):
    """Owner dashboard"""
    if request.user.role not in ['owner', 'admin']:
        messages.warning(request, 'This page is for property owners.')
        return redirect('dashboard:dashboard')
    
    properties = Property.objects.filter(owner=request.user)
    total_properties = properties.count()
    available = properties.filter(status='available').count()
    rented = properties.filter(status='rented').count()
    total_views = sum(p.views_count for p in properties)
    
    recent_inquiries = Inquiry.objects.filter(
        property__owner=request.user
    ).select_related('user', 'property').order_by('-created_at')[:10]
    
    unread_inquiries = Inquiry.objects.filter(
        property__owner=request.user,
        is_read=False
    ).count()
    
    context = {
        'total_properties': total_properties,
        'available': available,
        'rented': rented,
        'total_views': total_views,
        'recent_inquiries': recent_inquiries,
        'unread_inquiries': unread_inquiries,
        'properties': properties[:5],
    }
    return render(request, 'owner/dashboard.html', context)


# About & Contact pages
def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    return render(request, 'pages/contact.html')


def page_not_found(request, exception=None):
    return render(request, 'pages/404.html', status=404)
