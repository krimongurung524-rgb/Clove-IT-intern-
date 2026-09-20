from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:property_id>/', views.book_visit, name='book_visit'),
    path('my-visits/', views.my_visits, name='my_visits'),
    path('manage/<int:pk>/', views.manage_booking, name='manage'),
    path('cancel/<int:pk>/', views.cancel_booking, name='cancel'),
]
