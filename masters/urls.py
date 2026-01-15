from django.urls import path
from . import views

app_name = 'masters'

urlpatterns = [
    path('', views.master_list, name='master_list'),
    path('<int:pk>/', views.master_detail, name='master_detail'),
    path('service/<int:service_id>/', views.master_by_service, name='master_by_service'),
]
