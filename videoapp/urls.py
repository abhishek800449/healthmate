from django.urls import path
from . import views

urlpatterns = [
        path('book_consultation/<slug:specialization_slug>/', views.book_consultation, name='book_consultation'),
        path('booking_success/<slug:specialization_slug>/', views.booking, name='booking'),
        path('meeting/',views.videocall, name='meeting'),
        path('join/',views.join_room, name='join_room'),
]