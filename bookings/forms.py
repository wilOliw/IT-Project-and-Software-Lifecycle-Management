from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from services.models import Service
from masters.models import Master

class AppointmentForm(forms.ModelForm):
    """Форма записи на услугу"""
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        empty_label="Выберите услугу",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    master = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_active=True),
        empty_label="Любой мастер",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Дополнительные пожелания или примечания'
        }),
        required=False
    )
    
    class Meta:
        model = Appointment
        fields = ['service', 'master', 'appointment_date', 'start_time', 'notes']
    
    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        master = cleaned_data.get('master')
        appointment_date = cleaned_data.get('appointment_date')
        start_time = cleaned_data.get('start_time')
        
        if service and appointment_date and start_time:
            # Проверка, что дата не в прошлом
            if appointment_date < timezone.now().date():
                raise forms.ValidationError("Нельзя записаться на прошедшую дату")
            
            # Проверка, что время работы студии (9:00 - 21:00)
            if start_time < datetime.strptime('09:00', '%H:%M').time() or \
               start_time > datetime.strptime('21:00', '%H:%M').time():
                raise forms.ValidationError("Время записи должно быть с 9:00 до 21:00")
            
            # Проверка доступности времени
            if master:
                # Проверяем, не занято ли время у выбранного мастера
                end_time = self._calculate_end_time(service, start_time)
                if self._is_time_conflicting(master, appointment_date, start_time, end_time):
                    raise forms.ValidationError("Выбранное время уже занято у этого мастера")
        
        return cleaned_data
    
    def _calculate_end_time(self, service, start_time):
        """Рассчитывает время окончания услуги"""
        start_datetime = datetime.combine(timezone.now().date(), start_time)
        end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)
        return end_datetime.time()
    
    def _is_time_conflicting(self, master, date, start_time, end_time):
        """Проверяет, есть ли конфликт времени"""
        from .models import Appointment
        
        conflicting_appointments = Appointment.objects.filter(
            master=master,
            appointment_date=date,
            status__in=['pending', 'confirmed'],
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        return conflicting_appointments.exists()

class AppointmentFilterForm(forms.Form):
    """Форма фильтрации записей"""
    STATUS_CHOICES = [
        ('', 'Все статусы'),
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    master = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_active=True),
        required=False,
        empty_label="Все мастера",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        required=False,
        empty_label="Все услуги",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
