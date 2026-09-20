from django.contrib import admin
from .models import Property, PropertyImage, Inquiry, LocationUnlock


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'property_type', 'city', 'price', 'status', 'is_featured', 'views_count', 'created_at']
    list_filter = ['property_type', 'status', 'city', 'furnishing', 'is_featured', 'gender_preference']
    search_fields = ['title', 'address', 'city', 'area', 'owner__username']
    list_editable = ['status', 'is_featured']
    inlines = [PropertyImageInline]
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {'fields': ('owner', 'title', 'description', 'property_type', 'status', 'is_featured')}),
        ('Location', {'fields': ('address', 'city', 'area', 'landmark', 'latitude', 'longitude')}),
        ('Pricing', {'fields': ('price', 'deposit', 'price_negotiable', 'location_unlock_fee')}),
        ('Details', {'fields': ('bedrooms', 'bathrooms', 'area_sqft', 'floor', 'total_floors', 'furnishing', 'gender_preference')}),
        ('Amenities', {
            'fields': (
                'has_wifi', 'has_parking', 'has_kitchen', 'has_ac', 'has_water',
                'has_electricity', 'has_security', 'has_balcony', 'has_lift',
                'has_gym', 'pets_allowed', 'smoking_allowed'
            ),
            'classes': ('collapse',)
        }),
        ('Contact', {'fields': ('contact_phone', 'contact_whatsapp')}),
        ('Meta', {'fields': ('views_count', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['property__title', 'user__username', 'message']


@admin.register(LocationUnlock)
class LocationUnlockAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'amount', 'status', 'payment_method', 'paid_at', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['user__username', 'property__title', 'transaction_id']
    list_editable = ['status']
    readonly_fields = ['created_at']
