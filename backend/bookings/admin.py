from django.contrib import admin
from .models import VisitBooking


@admin.register(VisitBooking)
class VisitBookingAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'preferred_date', 'preferred_time', 'status', 'created_at']
    list_filter = ['status', 'preferred_date']
    search_fields = ['property__title', 'user__username']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
