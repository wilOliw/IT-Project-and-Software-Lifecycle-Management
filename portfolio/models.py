from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from masters.models import Master
from services.models import Service

class Portfolio(models.Model):
    """Портфолио работ мастера"""
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='portfolio_works', verbose_name=_('Мастер'))
    title = models.CharField(max_length=200, verbose_name=_('Название работы'))
    description = models.TextField(verbose_name=_('Описание работы'))
    image = models.ImageField(upload_to='portfolio/', verbose_name=_('Изображение'))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='portfolio_works', verbose_name=_('Услуга'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Рекомендуемое'))
    sort_order = models.IntegerField(default=0, verbose_name=_('Порядок сортировки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Работа в портфолио')
        verbose_name_plural = _('Работы в портфолио')
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return f"{self.master} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('portfolio:portfolio_detail', kwargs={'pk': self.pk})

class PortfolioImage(models.Model):
    """Дополнительные изображения для работы в портфолио"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='additional_images', verbose_name=_('Работа'))
    image = models.ImageField(upload_to='portfolio/additional/', verbose_name=_('Изображение'))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_('Подпись'))
    sort_order = models.IntegerField(default=0, verbose_name=_('Порядок сортировки'))
    
    class Meta:
        verbose_name = _('Дополнительное изображение')
        verbose_name_plural = _('Дополнительные изображения')
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Изображение для {self.portfolio.title}"
