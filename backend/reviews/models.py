from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from properties.models import Property


class Review(models.Model):
    """Property reviews and ratings"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=100, blank=True)
    comment = models.TextField()
    is_verified = models.BooleanField(default=False, help_text="Verified stay")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('property', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rating}★ by {self.user.username} on {self.property.title}"
