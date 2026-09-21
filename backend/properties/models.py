from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class Property(models.Model):
    PROPERTY_TYPES = (
        ('room', 'Single Room'),
        ('flat', 'Flat/Apartment'),
        ('house', 'House'),
        ('hostel', 'Hostel'),
        ('pg', 'PG / Paying Guest'),
        ('studio', 'Studio Apartment'),
    )
    FURNISHING = (
        ('furnished', 'Fully Furnished'),
        ('semi', 'Semi Furnished'),
        ('unfurnished', 'Unfurnished'),
    )
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('pending', 'Pending'),
        ('inactive', 'Inactive'),
    )
    GENDER_PREF = (
        ('any', 'Any'),
        ('male', 'Male Only'),
        ('female', 'Female Only'),
        ('family', 'Family Only'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='room')

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100, blank=True, help_text='Neighborhood / Area')
    landmark = models.CharField(max_length=150, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Security deposit')
    price_negotiable = models.BooleanField(default=False)
    location_unlock_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=50,
        blank=True,                                    # ← FIX: yo matra thapiyeko
        validators=[MinValueValidator(0)],
        help_text='Amount user must pay to see exact location'
    )

    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    area_sqft = models.PositiveIntegerField(blank=True, null=True, help_text='Area in square feet')
    floor = models.CharField(max_length=20, blank=True, help_text='e.g. 2nd Floor')
    total_floors = models.PositiveIntegerField(blank=True, null=True)
    furnishing = models.CharField(max_length=20, choices=FURNISHING, default='unfurnished')
    gender_preference = models.CharField(max_length=10, choices=GENDER_PREF, default='any')

    has_wifi = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_kitchen = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_water = models.BooleanField(default=True)
    has_electricity = models.BooleanField(default=True)
    has_security = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    has_lift = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    smoking_allowed = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    contact_phone = models.CharField(max_length=15, blank=True)
    contact_whatsapp = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.city} (Rs. {self.price})'

    def get_absolute_url(self):
        return reverse('properties:details', kwargs={'pk': self.pk})

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @property
    def main_image(self):
        first = self.images.first()
        if first:
            return first.image.url
        return '/static/images/rooms/default-room.jpg'

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()

    def get_amenities_list(self):
        amenities = []
        if self.has_wifi: amenities.append('WiFi')
        if self.has_parking: amenities.append('Parking')
        if self.has_kitchen: amenities.append('Kitchen')
        if self.has_ac: amenities.append('AC')
        if self.has_water: amenities.append('Water')
        if self.has_electricity: amenities.append('Electricity')
        if self.has_security: amenities.append('Security')
        if self.has_balcony: amenities.append('Balcony')
        if self.has_lift: amenities.append('Lift')
        if self.has_gym: amenities.append('Gym')
        if self.pets_allowed: amenities.append('Pets Allowed')
        if self.smoking_allowed: amenities.append('Smoking Allowed')
        return amenities

    def public_location_label(self):
        parts = [p for p in [self.area, self.city] if p]
        return ', '.join(parts) if parts else (self.city or 'Location hidden')

    def user_can_see_exact_location(self, user):
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        if self.owner_id == user.id:
            return True
        return self.location_unlocks.filter(user=user, status='paid').exists()


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        return f'Image for {self.property.title}'


class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField()
    phone = models.CharField(max_length=15, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Inquiries'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'Inquiry by {self.user.username} on {self.property.title}'


class LocationUnlock(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location_unlocks')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='location_unlocks')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, default='demo')
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.property.title} ({self.status})'
