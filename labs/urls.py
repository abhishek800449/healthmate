from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_test, name='booking_test'),
    path('ajax/get_test_details/', views.get_test_details, name='get_test_details'),
]