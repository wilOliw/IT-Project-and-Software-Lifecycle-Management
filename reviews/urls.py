from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('create/', views.review_create, name='review_create'),
    path('<int:pk>/', views.review_detail, name='review_detail'),
    path('<int:pk>/edit/', views.review_edit, name='review_edit'),
    path('<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('<int:pk>/response/', views.review_response_create, name='review_response'),
    path('master/<int:master_id>/', views.master_reviews, name='master_reviews'),
    path('service/<int:service_id>/', views.service_reviews, name='service_reviews'),
    path('stats/', views.review_stats, name='review_stats'),
]
