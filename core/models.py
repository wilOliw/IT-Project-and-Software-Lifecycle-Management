from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    """Профиль пользователя с дополнительной информацией"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Телефон'))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('Дата рождения'))
    address = models.TextField(blank=True, verbose_name=_('Адрес'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')
    
    def __str__(self):
        return f"Профиль {self.user.get_full_name() or self.user.username}"

class Contact(models.Model):
    """Контактная информация студии"""
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    value = models.CharField(max_length=255, verbose_name=_('Значение'))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('Иконка'))
    order = models.IntegerField(default=0, verbose_name=_('Порядок'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    
    class Meta:
        verbose_name = _('Контакт')
        verbose_name_plural = _('Контакты')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name}: {self.value}"

class News(models.Model):
    """Новости и акции студии"""
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Содержание'))
    image = models.ImageField(upload_to='news/', blank=True, verbose_name=_('Изображение'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Рекомендуемое'))
    
    class Meta:
        verbose_name = _('Новость')
        verbose_name_plural = _('Новости')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class About(models.Model):
    """Информация о студии"""
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Содержание'))
    image = models.ImageField(upload_to='about/', blank=True, verbose_name=_('Изображение'))
    order = models.IntegerField(default=0, verbose_name=_('Порядок'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    
    class Meta:
        verbose_name = _('О студии')
        verbose_name_plural = _('О студии')
        ordering = ['order']
    
    def __str__(self):
        return self.title
