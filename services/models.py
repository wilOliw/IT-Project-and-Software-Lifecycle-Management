from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class Category(models.Model):
    """Категория услуг"""
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Иконка'))
    image = models.ImageField(upload_to='categories/', blank=True, verbose_name=_('Изображение'))
    sort_order = models.IntegerField(default=0, verbose_name=_('Порядок сортировки'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    
    class Meta:
        verbose_name = _('Категория услуг')
        verbose_name_plural = _('Категории услуг')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('services:category_detail', kwargs={'pk': self.pk})

class Service(models.Model):
    """Услуга студии красоты"""
    name = models.CharField(max_length=200, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'))
    short_description = models.CharField(max_length=300, blank=True, verbose_name=_('Краткое описание'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    duration_minutes = models.IntegerField(verbose_name=_('Длительность (минуты)'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services', verbose_name=_('Категория'))
    image = models.ImageField(upload_to='services/', blank=True, verbose_name=_('Изображение'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Рекомендуемое'))
    sort_order = models.IntegerField(default=0, verbose_name=_('Порядок сортировки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Услуга')
        verbose_name_plural = _('Услуги')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={'pk': self.pk})
    
    def get_duration_display(self):
        """Возвращает отформатированную длительность услуги"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0 and minutes > 0:
            return f"{hours}ч {minutes}мин"
        elif hours > 0:
            return f"{hours}ч"
        else:
            return f"{minutes}мин"
    
    def get_price_display(self):
        """Возвращает отформатированную цену"""
        return f"{self.price} ₽"
