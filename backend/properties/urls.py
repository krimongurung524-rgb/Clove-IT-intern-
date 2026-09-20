from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('map/', views.map_view, name='map'),
    path('<int:pk>/', views.property_details, name='details'),
    path('<int:pk>/unlock-location/', views.unlock_location, name='unlock_location'),
    path('add/', views.add_property, name='add'),
    path('<int:pk>/edit/', views.edit_property, name='edit'),
    path('<int:pk>/delete/', views.delete_property, name='delete'),
    path('my-properties/', views.my_properties, name='my_properties'),
]
