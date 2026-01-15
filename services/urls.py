from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('price/', views.price_list, name='price_list'),
]
