from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from properties.models import Property
from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Check if already reviewed
    existing = Review.objects.filter(property=property_obj, user=request.user).first()
    if existing:
        messages.info(request, 'You have already reviewed this property.')
        return redirect('properties:details', pk=property_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = property_obj
            review.user = request.user
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('properties:details', pk=property_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'property': property_obj,
    }
    return render(request, 'properties/details.html', context)  # Modal preferred


@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated!')
            return redirect('properties:details', pk=review.property.pk)
    else:
        form = ReviewForm(instance=review)
    
    return redirect('properties:details', pk=review.property.pk)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    property_id = review.property.pk
    if request.method == 'POST':
        review.delete()
        messages.info(request, 'Review deleted.')
    return redirect('properties:details', pk=property_id)
