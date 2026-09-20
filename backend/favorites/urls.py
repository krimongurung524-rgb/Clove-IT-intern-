from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('toggle/<int:property_id>/', views.toggle_favorite, name='toggle'),
    path('saved/', views.saved_rooms, name='saved'),
]
