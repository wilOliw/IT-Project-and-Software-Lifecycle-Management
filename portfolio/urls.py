from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('featured/', views.featured_portfolio, name='featured_portfolio'),
    path('<int:pk>/', views.portfolio_detail, name='portfolio_detail'),
    path('master/<int:master_id>/', views.master_portfolio, name='master_portfolio'),
    path('service/<int:service_id>/', views.service_portfolio, name='service_portfolio'),
]
