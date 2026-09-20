from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:property_id>/', views.add_review, name='add'),
    path('edit/<int:pk>/', views.edit_review, name='edit'),
    path('delete/<int:pk>/', views.delete_review, name='delete'),
]
