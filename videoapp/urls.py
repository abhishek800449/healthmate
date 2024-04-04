from django.urls import path
from . import views

urlpatterns = [
        path('meeting/',views.videocall, name='meeting'),
        path('join/',views.join_room, name='join_room'),
]