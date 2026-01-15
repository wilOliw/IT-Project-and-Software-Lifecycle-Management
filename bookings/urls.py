from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/edit/', views.appointment_edit, name='appointment_edit'),
    path('<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('available-times/', views.available_times, name='available_times'),
    
    # Административные маршруты
    path('admin/', views.admin_appointment_list, name='admin_appointment_list'),
    path('admin/<int:pk>/edit/', views.admin_appointment_edit, name='admin_appointment_edit'),
]
