from django.contrib import admin
from .models import Portfolio, PortfolioImage

class PortfolioImageInline(admin.TabularInline):
    """Встроенное редактирование дополнительных изображений"""
    model = PortfolioImage
    extra = 1
    fields = ['image', 'caption', 'sort_order']

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'master', 'service', 'is_active', 
        'is_featured', 'sort_order', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'service__category', 'created_at']
    list_editable = ['is_active', 'is_featured', 'sort_order']
    search_fields = ['title', 'description', 'master__user__first_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PortfolioImageInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('master', 'title', 'description', 'service')
        }),
        ('Изображения', {
            'fields': ('image',)
        }),
        ('Настройки', {
            'fields': ('is_active', 'is_featured', 'sort_order')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'caption', 'sort_order']
    list_editable = ['sort_order']
    search_fields = ['portfolio__title', 'caption']
