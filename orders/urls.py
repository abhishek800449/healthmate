from django.urls import path
from . import views

urlpatterns = [
    path('booking_success/', views.booking_success, name='booking_success'),
    path('lab_checkout/', views.lab_checkout, name='lab_checkout'),
    path('lab_success/', views.lab_success, name='lab_success'),
    path('<slug:doctor_slug>/', views.checkout, name='checkout'),
    path('view_invoice/<int:order_id>/', views.view_invoice, name='view_invoice'),
    path('book_consultation/<slug:specialization_slug>/', views.book_consultation, name='book_consultation'),
    path('booking_success/<slug:specialization_slug>/', views.booking, name='booking'),
]