from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from services.models import Service
from masters.models import Master

class Appointment(models.Model):
    """Запись клиента на услугу"""
    STATUS_CHOICES = [
        ('pending', _('Ожидает подтверждения')),
        ('confirmed', _('Подтверждено')),
        ('completed', _('Завершено')),
        ('cancelled', _('Отменено')),
        ('no_show', _('Не явился')),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', verbose_name=_('Клиент'))
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='appointments', verbose_name=_('Мастер'))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments', verbose_name=_('Услуга'))
    appointment_date = models.DateField(verbose_name=_('Дата записи'))
    start_time = models.TimeField(verbose_name=_('Время начала'))
    end_time = models.TimeField(verbose_name=_('Время окончания'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Статус'))
    notes = models.TextField(blank=True, verbose_name=_('Примечания'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Запись')
        verbose_name_plural = _('Записи')
        ordering = ['-appointment_date', '-start_time']
        unique_together = ['master', 'appointment_date', 'start_time']
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.service.name} у {self.master} {self.appointment_date} {self.start_time}"
    
    def clean(self):
        """Валидация записи"""
        if self.appointment_date < timezone.now().date():
            raise ValidationError(_('Нельзя записаться на прошедшую дату'))
        
        # Проверяем время только если end_time установлено
        if self.end_time and self.start_time >= self.end_time:
            raise ValidationError(_('Время начала должно быть раньше времени окончания'))
        
        # Проверка на пересечение с другими записями (только если end_time установлено)
        if self.end_time:
            overlapping_appointments = Appointment.objects.filter(
                master=self.master,
                appointment_date=self.appointment_date,
                status__in=['pending', 'confirmed'],
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk)
            
            if overlapping_appointments.exists():
                raise ValidationError(_('Выбранное время уже занято'))
    
    def save(self, *args, **kwargs):
        """Автоматический расчет времени окончания"""
        if not self.end_time and self.start_time and self.service:
            # Получаем длительность услуги у конкретного мастера
            try:
                from masters.models import MasterService
                master_service = MasterService.objects.get(master=self.master, service=self.service)
                duration = master_service.get_final_duration()
            except MasterService.DoesNotExist:
                duration = self.service.duration_minutes
            
            start_datetime = datetime.combine(self.appointment_date, self.start_time)
            end_datetime = start_datetime + timedelta(minutes=duration)
            self.end_time = end_datetime.time()
        
        super().save(*args, **kwargs)
    
    def get_duration(self):
        """Возвращает длительность записи в минутах"""
        start = datetime.combine(self.appointment_date, self.start_time)
        end = datetime.combine(self.appointment_date, self.end_time)
        return int((end - start).total_seconds() / 60)
    
    def get_status_display_class(self):
        """Возвращает CSS класс для статуса"""
        status_classes = {
            'pending': 'warning',
            'confirmed': 'info',
            'completed': 'success',
            'cancelled': 'danger',
            'no_show': 'secondary',
        }
        return status_classes.get(self.status, 'secondary')

class TimeSlot(models.Model):
    """Временные слоты для записи"""
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='time_slots', verbose_name=_('Мастер'))
    date = models.DateField(verbose_name=_('Дата'))
    start_time = models.TimeField(verbose_name=_('Время начала'))
    end_time = models.TimeField(verbose_name=_('Время окончания'))
    is_available = models.BooleanField(default=True, verbose_name=_('Доступно'))
    is_break = models.BooleanField(default=False, verbose_name=_('Перерыв'))
    
    class Meta:
        verbose_name = _('Временной слот')
        verbose_name_plural = _('Временные слоты')
        unique_together = ['master', 'date', 'start_time']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.master} - {self.date} {self.start_time}-{self.end_time}"
    
    def is_booked(self):
        """Проверяет, забронирован ли слот"""
        return Appointment.objects.filter(
            master=self.master,
            appointment_date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=['pending', 'confirmed']
        ).exists()

class MasterService(models.Model):
    """Связь мастер-услуга для приложения bookings"""
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='booking_masterservices', verbose_name=_('Мастер'))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='booking_masterservices', verbose_name=_('Услуга'))
    price_modifier = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.00, 
        verbose_name=_('Модификатор цены')
    )
    duration_modifier = models.IntegerField(
        default=0, 
        verbose_name=_('Модификатор длительности (минуты)')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    
    class Meta:
        verbose_name = _('Услуга мастера')
        verbose_name_plural = _('Услуги мастеров')
        unique_together = ['master', 'service']
    
    def __str__(self):
        return f"{self.master} - {self.service}"
    
    def get_final_price(self):
        """Возвращает итоговую цену услуги у мастера"""
        return self.service.price * self.price_modifier
    
    def get_final_duration(self):
        """Возвращает итоговую длительность услуги у мастера"""
        return self.service.duration_minutes + self.duration_modifier
