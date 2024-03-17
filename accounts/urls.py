from django.urls import path
from . import views

urlpatterns = [
    # post views
    path('patient_register/', views.patient_register, name='patient_register'),
    path('doctor_register/', views.doctor_register, name='doctor_register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient_profile/', views.patient_profile, name='patient_profile'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('schedule_time/', views.schedule_time, name='schedule_time'),
    path('delete_timeslot/<int:timeslot_id>/', views.delete_timeslot, name='delete_timeslot'),
    path('view_appointments/', views.view_appointments, name='view_appointments'),
    path('my_appointments/', views.my_appointments, name='my_appointments'),
    path('view_patient/<str:patient_username>/', views.view_patient, name='view_patient'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_doctor_password/', views.change_doctor_password, name='change_doctor_password'),
    path('save_record/', views.save_record, name='save_record'),
    path('view_file/<int:id>/', views.view_file, name='view_file'),
    path('delete_record/<int:medical_id>/', views.delete_record, name='delete_record'),
    #path('dashboard/', views.dashboard, name='dashboard'),
    #path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    #path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    #path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    #path('resetPassword/', views.resetPassword, name='resetPassword'),

    #path('my_orders/', views.my_orders, name='my_orders'),
    #path('edit_profile/', views.edit_profile, name='edit_profile'),
    #path('change_password/', views.change_password, name='change_password'),
    #path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    #path('billing_address/', views.billing_address, name='billing_address'),
    #path('ajax/get_states/', views.get_states, name='get_states'),
    #path('ajax/get_cities/', views.get_cities, name='get_cities'),
]