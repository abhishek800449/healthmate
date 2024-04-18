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
    path('specialities/', views.adminapp_specialities, name='adminapp_specialities'),
    path('delete_specialization/', views.delete_specialization, name='delete_specialization'),
    path('edit_specialization/', views.edit_specialization, name='edit_specialization'),
    path('reviews/', views.adminapp_reviews, name='adminapp_reviews'), 
    path('delete_review/', views.delete_review, name='delete_review'),
    path('transactions/', views.adminapp_transactions, name='adminapp_transactions'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('lab_appointments/', views.adminapp_lab_appointments, name='adminapp_lab_appointments'),
    path('edit_lab_appointments/<int:id>/', views.edit_lab_appointments, name='edit_lab_appointments'),
    path('add_lab_results/<int:id>/', views.add_lab_results, name='add_lab_results'),
    path('lab_tests/', views.adminapp_lab_tests, name='adminapp_lab_tests'),
    path('delete_lab_tests/', views.delete_lab_tests, name='delete_lab_tests'),
    path('forgotPassword/', views.forgotAdminPassword, name='forgotAdminPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetAdminpassword_validate, name='resetAdminpassword_validate'),
    path('resetPassword/', views.resetAdminPassword, name='resetAdminPassword'),
]