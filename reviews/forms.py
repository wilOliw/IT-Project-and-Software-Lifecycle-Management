from django import forms

from bookings.models import Appointment
from .models import Review, ReviewResponse
from masters.models import Master
from services.models import Service

class ReviewForm(forms.ModelForm):
    """Форма создания отзыва"""

    rating = forms.ChoiceField(
        choices=[(i, f"{i} звезд") for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'rating-input'}),
        label='Оценка'
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Поделитесь своими впечатлениями об услуге и мастере...'
        }),
        label='Комментарий'
    )
    
    class Meta:
        model = Review
        fields = ['master', 'service', 'rating', 'comment']
        widgets = {
            'master': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только активных мастеров и услуги
        self.fields['master'].queryset = Master.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

class ReviewResponseForm(forms.ModelForm):
    """Форма ответа мастера на отзыв"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ответьте на отзыв клиента...'
        }),
        label='Ответ'
    )
    
    class Meta:
        model = ReviewResponse
        fields = ['content']

class ReviewFilterForm(forms.Form):
    """Форма фильтрации отзывов"""
    RATING_CHOICES = [
        ('', 'Все оценки'),
        ('5', '5 звезд'),
        ('4', '4 звезды'),
        ('3', '3 звезды'),
        ('2', '2 звезды'),
        ('1', '1 звезда'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
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
    
    verified_only = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Только подтвержденные'
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('newest', 'Сначала новые'),
            ('oldest', 'Сначала старые'),
            ('rating_high', 'По убыванию рейтинга'),
            ('rating_low', 'По возрастанию рейтинга'),
        ],
        required=False,
        initial='newest',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
