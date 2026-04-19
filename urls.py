from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Public URLs
    path('category/<int:category_id>/', views.category_businesses, name='category_businesses'),
    path('business/<int:profile_id>/', views.business_detail, name='business_detail'),

    # Client URLs
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('client/book_appointment/', views.book_appointment, name='book_appointment'),
    path('client/appointments/', views.client_appointments, name='client_appointments'),
    path('client/cancel_appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('client/profile/', views.client_profile, name='client_profile'),
    path('client/respond_to_reschedule/<int:appointment_id>/', views.respond_to_reschedule, name='respond_to_reschedule'),

    # Business URLs
    path('business/dashboard/', views.business_dashboard, name='business_dashboard'),
    path('business/update_appointment_status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),
    path('business/reschedule_appointment/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('business/add_service/', views.add_service, name='add_service'),
    path('business/manage_services/', views.manage_services, name='manage_services'),
    path('business/edit_service/<int:service_id>/', views.edit_service, name='edit_service'),
    path('business/delete_service/<int:service_id>/', views.delete_service, name='delete_service'),
    path('business/manage_availability/<int:service_id>/', views.manage_availability, name='manage_availability'),
    path('business/delete_availability_slot/<int:service_id>/<int:slot_id>/', views.delete_availability_slot, name='delete_availability_slot'),
    path('business/profile/', views.business_profile_view, name='business_profile_view'),
]