from django.contrib import admin
from .models import Master, MasterService, MasterSchedule

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'experience_years', 'is_active', 'sort_order']
    list_filter = ['is_active', 'specialization']
    list_editable = ['is_active', 'sort_order']
    search_fields = ['user__first_name', 'user__last_name', 'specialization']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(MasterService)
class MasterServiceAdmin(admin.ModelAdmin):
    list_display = ['master', 'service', 'price_modifier', 'duration_modifier', 'is_active']
    list_filter = ['is_active', 'service__category']
    list_editable = ['price_modifier', 'duration_modifier', 'is_active']
    search_fields = ['master__user__first_name', 'service__name']

@admin.register(MasterSchedule)
class MasterScheduleAdmin(admin.ModelAdmin):
    list_display = ['master', 'day_of_week', 'start_time', 'end_time', 'is_working_day']
    list_filter = ['day_of_week', 'is_working_day']
    list_editable = ['start_time', 'end_time', 'is_working_day']
    search_fields = ['master__user__first_name']
