from django.contrib import admin
from .models import Appointment, TimeSlot, MasterService

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'client', 'master', 'service', 'appointment_date', 
        'start_time', 'end_time', 'status', 'created_at'
    ]
    list_filter = ['status', 'appointment_date', 'master', 'service']
    list_editable = ['status']
    search_fields = [
        'client__username', 'client__first_name', 'client__last_name',
        'master__user__first_name', 'master__user__last_name',
        'service__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'appointment_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('client', 'master', 'service', 'status')
        }),
        ('Время записи', {
            'fields': ('appointment_date', 'start_time', 'end_time')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['master', 'date', 'start_time', 'end_time', 'is_available', 'is_break']
    list_filter = ['date', 'is_available', 'is_break', 'master']
    list_editable = ['is_available', 'is_break']
    search_fields = ['master__user__first_name', 'master__user__last_name']
    date_hierarchy = 'date'

@admin.register(MasterService)
class MasterServiceAdmin(admin.ModelAdmin):
    list_display = ['master', 'service', 'price_modifier', 'duration_modifier', 'is_active']
    list_filter = ['is_active', 'service__category']
    list_editable = ['price_modifier', 'duration_modifier', 'is_active']
    search_fields = ['master__user__first_name', 'service__name']
