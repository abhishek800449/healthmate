from django.urls import path
from . import views

urlpatterns = [
    # post views
    path('', views.index, name='index'),
    path('register/', views.adminapp_register, name='adminapp_register'),
    path('login/', views.adminapp_login, name='adminapp_login'),
    path('logout/', views.adminapp_logout, name='adminapp_logout'),
    path('profile/', views.adminapp_profile, name='adminapp_profile'),
    path('change_password/', views.adminapp_change_password, name='adminapp_change_password'),
    path('doctor_list/', views.adminapp_doctor_list, name='adminapp_doctor_list'),
    path('patient_list/', views.adminapp_patient_list, name='adminapp_patient_list'),
    path('ajax/change_status/', views.change_status, name='change_status'),
]