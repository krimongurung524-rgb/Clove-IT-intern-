from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversations_list, name='list'),
    path('<int:pk>/', views.conversation_detail, name='conversation'),
    path('start/<int:user_id>/', views.start_conversation, name='start'),
    path('start/<int:user_id>/<int:property_id>/', views.start_conversation, name='start_with_property'),
    path('send/<int:pk>/', views.send_message_ajax, name='send_ajax'),
]
