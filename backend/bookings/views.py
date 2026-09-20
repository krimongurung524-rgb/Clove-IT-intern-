from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from properties.models import Property
from .models import VisitBooking
from .forms import VisitBookingForm


@login_required
def book_visit(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id, status='available')
    
    # Prevent owner from booking own property
    if property_obj.owner == request.user:
        messages.error(request, "You cannot book a visit to your own property.")
        return redirect('properties:details', pk=property_id)
    
    if request.method == 'POST':
        form = VisitBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.property = property_obj
            booking.user = request.user
            booking.save()
            messages.success(request, 'Visit request submitted! The owner will confirm soon.')
            return redirect('dashboard:visits')
    else:
        form = VisitBookingForm()
    
    context = {
        'form': form,
        'property': property_obj,
    }
    return render(request, 'dashboard/visits.html', context)  # Will handle via modal or separate


@login_required
def my_visits(request):
    """Tenant: View own visit bookings"""
    bookings = VisitBooking.objects.filter(user=request.user).select_related('property', 'property__owner')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'dashboard/visits.html', context)


@login_required
def manage_booking(request, pk):
    """Owner: Confirm/Reject a booking"""
    booking = get_object_or_404(VisitBooking, pk=pk, property__owner=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            booking.status = 'confirmed'
            messages.success(request, 'Visit confirmed!')
        elif action == 'reject':
            booking.status = 'rejected'
            messages.info(request, 'Visit request rejected.')
        elif action == 'complete':
            booking.status = 'completed'
            messages.success(request, 'Visit marked as completed.')
        booking.owner_notes = request.POST.get('notes', '')
        booking.save()
        return redirect('owner:dashboard')
    
    return redirect('owner:dashboard')


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(VisitBooking, pk=pk, user=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.info(request, 'Visit booking cancelled.')
    return redirect('dashboard:visits')
