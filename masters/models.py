from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from services.models import Service

class Master(models.Model):
    """Мастер студии красоты"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master_profile')
    specialization = models.CharField(max_length=200, verbose_name=_('Специализация'))
    experience_years = models.IntegerField(verbose_name=_('Опыт работы (лет)'))
    bio = models.TextField(verbose_name=_('Биография'))
    photo = models.ImageField(upload_to='masters/', blank=True, verbose_name=_('Фотография'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    sort_order = models.IntegerField(default=0, verbose_name=_('Порядок сортировки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    # Связь многие-ко-многим с услугами
    services = models.ManyToManyField(Service, through='MasterService', related_name='masters')
    
    class Meta:
        verbose_name = _('Мастер')
        verbose_name_plural = _('Мастера')
        ordering = ['sort_order', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"
    
    def get_absolute_url(self):
        return reverse('masters:master_detail', kwargs={'pk': self.pk})
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def get_services_display(self):
        """Возвращает список услуг мастера"""
        return ", ".join([service.name for service in self.services.filter(is_active=True)])

class MasterService(models.Model):
    """Связь мастер-услуга с дополнительными параметрами"""
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='master_masterservices', verbose_name=_('Мастер'))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='master_masterservices', verbose_name=_('Услуга'))
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

class MasterSchedule(models.Model):
    """Расписание работы мастера"""
    DAYS_OF_WEEK = [
        (1, _('Понедельник')),
        (2, _('Вторник')),
        (3, _('Среда')),
        (4, _('Четверг')),
        (5, _('Пятница')),
        (6, _('Суббота')),
        (7, _('Воскресенье')),
    ]
    
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='schedule', verbose_name=_('Мастер'))
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name=_('День недели'))
    start_time = models.TimeField(verbose_name=_('Время начала'))
    end_time = models.TimeField(verbose_name=_('Время окончания'))
    is_working_day = models.BooleanField(default=True, verbose_name=_('Рабочий день'))
    
    class Meta:
        verbose_name = _('Расписание мастера')
        verbose_name_plural = _('Расписание мастеров')
        unique_together = ['master', 'day_of_week']
        ordering = ['master', 'day_of_week']
    
    def __str__(self):
        return f"{self.master} - {self.get_day_of_week_display()}"
