from django.urls import path
from . import views

urlpatterns = [
    #path('schedule_time/', views.schedule_time, name='schedule_time'),
    #path('doctor_register/', views.doctor_register, name='doctor_register'),
    path('', views.doctors_list, name='doctors_list'),
    path('filter_results/', views.filter_results, name='filter_results'),
    path('specialization/<slug:specialization_slug>/', views.doctors_list, name='doctors_by_specialization'),
    path('specialization/<slug:specialization_slug>/<slug:doctor_slug>/', views.view_doctor, name='view_doctor'),
    path('specialization/<slug:specialization_slug>/<slug:doctor_slug>/book_appointment/', views.book_appointment, name='book_appointment'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:doctor_id>/', views.submit_review, name='submit_review'),
]