from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from masters.models import Master
from services.models import Service

class Review(models.Model):
    """Отзыв клиента о мастере или услуге"""
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Клиент'))
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Мастер'))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Услуга'))
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Оценка')
    )
    comment = models.TextField(verbose_name=_('Комментарий'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Подтверждено'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']
        unique_together = ['client', 'master', 'service']
    
    def __str__(self):
        return f"Отзыв от {self.client.get_full_name()} о {self.master} - {self.rating}/5"
    
    def get_absolute_url(self):
        return reverse('reviews:review_detail', kwargs={'pk': self.pk})
    
    def get_rating_display(self):
        """Возвращает отображение рейтинга звездочками"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def get_rating_class(self):
        """Возвращает CSS класс для рейтинга"""
        if self.rating >= 4:
            return 'text-success'
        elif self.rating >= 3:
            return 'text-warning'
        else:
            return 'text-danger'

class ReviewImage(models.Model):
    """Изображения к отзыву"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images', verbose_name=_('Отзыв'))
    image = models.ImageField(upload_to='reviews/', verbose_name=_('Изображение'))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_('Подпись'))
    sort_order = models.IntegerField(default=0, verbose_name=_('Порядок сортировки'))
    
    class Meta:
        verbose_name = _('Изображение отзыва')
        verbose_name_plural = _('Изображения отзывов')
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Изображение для отзыва {self.review.pk}"

class ReviewResponse(models.Model):
    """Ответ мастера на отзыв"""
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response', verbose_name=_('Отзыв'))
    master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name=_('Мастер'))
    content = models.TextField(verbose_name=_('Содержание ответа'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Ответ на отзыв')
        verbose_name_plural = _('Ответы на отзывы')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ответ на отзыв {self.review.pk} от {self.master}"
