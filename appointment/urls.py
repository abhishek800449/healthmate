from django.urls import path
from . import views

urlpatterns = [
    #path('schedule_time/', views.schedule_time, name='schedule_time'),
    #path('doctor_register/', views.doctor_register, name='doctor_register'),
    path('', views.doctors_list, name='doctors_list'),
    path('specialization/<slug:specialization_slug>/', views.doctors_list, name='doctors_by_specialization'),
    path('specialization/<slug:specialization_slug>/<slug:doctor_slug>/', views.view_doctor, name='view_doctor'),
    path('specialization/<slug:specialization_slug>/<slug:doctor_slug>/book_appointment/', views.book_appointment, name='book_appointment'),
    path('checkout/booking_success/', views.booking_success, name='booking_success'),
    path('checkout/<slug:doctor_slug>/', views.checkout, name='checkout'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:doctor_id>/', views.submit_review, name='submit_review'),
    path('view_invoice/<int:order_id>/', views.view_invoice, name='view_invoice'),
]