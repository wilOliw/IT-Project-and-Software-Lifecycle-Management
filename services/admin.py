from django.contrib import admin
from .models import Category, Service

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['sort_order', 'is_active']
    search_fields = ['name', 'description']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'duration_minutes', 'is_active', 'is_featured']
    list_filter = ['category', 'is_active', 'is_featured']
    list_editable = ['price', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
