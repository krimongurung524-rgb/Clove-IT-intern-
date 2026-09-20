from django.db import models
from django.conf import settings
from django.utils import timezone
from properties.models import Property


class VisitBooking(models.Model):
    """Schedule a visit to a property"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    message = models.TextField(blank=True, help_text="Any special requests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    owner_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Visit Booking'
        verbose_name_plural = 'Visit Bookings'
    
    def __str__(self):
        return f"Visit by {self.user.username} to {self.property.title} on {self.preferred_date}"
    
    def is_upcoming(self):
        """Check if visit is still upcoming"""
        return self.preferred_date >= timezone.now().date() and self.status in ['pending', 'confirmed']
