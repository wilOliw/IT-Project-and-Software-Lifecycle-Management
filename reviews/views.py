from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .models import Review, ReviewResponse
from .forms import ReviewForm, ReviewResponseForm, ReviewFilterForm
from masters.models import Master
from services.models import Service

def review_list(request):
    """Список всех отзывов"""
    reviews = Review.objects.filter(is_active=True)
    
    # Фильтрация
    filter_form = ReviewFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('rating'):
            reviews = reviews.filter(rating=filter_form.cleaned_data['rating'])
        if filter_form.cleaned_data.get('master'):
            reviews = reviews.filter(master=filter_form.cleaned_data['master'])
        if filter_form.cleaned_data.get('service'):
            reviews = reviews.filter(service=filter_form.cleaned_data['service'])
        if filter_form.cleaned_data.get('verified_only'):
            reviews = reviews.filter(is_verified=True)
    
    # Сортировка
    sort_by = filter_form.cleaned_data.get('sort_by', 'newest')
    if sort_by == 'oldest':
        reviews = reviews.order_by('created_at')
    elif sort_by == 'rating_high':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort_by == 'rating_low':
        reviews = reviews.order_by('rating', '-created_at')
    else:
        reviews = reviews.order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Статистика
    total_reviews = Review.objects.filter(is_active=True).count()
    avg_rating = Review.objects.filter(is_active=True).aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'reviews': page_obj,
        'filter_form': filter_form,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'reviews/review_list.html', context)

def review_detail(request, pk):
    """Детальная страница отзыва"""
    review = get_object_or_404(Review, pk=pk, is_active=True)
    
    # Похожие отзывы
    related_reviews = Review.objects.filter(
        master=review.master,
        is_active=True
    ).exclude(pk=pk)[:3]
    
    context = {
        'review': review,
        'related_reviews': related_reviews,
    }
    return render(request, 'reviews/review_detail.html', context)

@login_required
def review_create(request):
    """Создание нового отзыва"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = request.user
            
            # Проверяем, не оставлял ли пользователь уже отзыв
            existing_review = Review.objects.filter(
                client=request.user,
                master=review.master,
                service=review.service
            ).first()
            
            if existing_review:
                messages.error(request, 'Вы уже оставляли отзыв для этой услуги у этого мастера')
                return redirect('reviews:review_list')
            
            review.save()
            messages.success(request, 'Отзыв успешно добавлен!')
            return redirect('reviews:review_detail', pk=review.pk)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
    }
    return render(request, 'reviews/review_create.html', context)

@login_required
def review_edit(request, pk):
    """Редактирование отзыва"""
    review = get_object_or_404(Review, pk=pk, client=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв успешно обновлен!')
            return redirect('reviews:review_detail', pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'reviews/review_edit.html', context)

@login_required
def review_delete(request, pk):
    """Удаление отзыва"""
    review = get_object_or_404(Review, pk=pk, client=request.user)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв успешно удален!')
        return redirect('reviews:review_list')
    
    context = {
        'review': review,
    }
    return render(request, 'reviews/review_delete.html', context)

def master_reviews(request, master_id):
    """Отзывы о конкретном мастере"""
    master = get_object_or_404(Master, pk=master_id, is_active=True)
    reviews = Review.objects.filter(master=master, is_active=True)
    
    # Статистика мастера
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    rating_distribution = reviews.values('rating').annotate(count=Count('rating')).order_by('rating')
    
    # Пагинация
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'master': master,
        'reviews': page_obj,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
    }
    return render(request, 'reviews/master_reviews.html', context)

def service_reviews(request, service_id):
    """Отзывы о конкретной услуге"""
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    reviews = Review.objects.filter(service=service, is_active=True)
    
    # Статистика услуги
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Пагинация
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'service': service,
        'reviews': page_obj,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'reviews/service_reviews.html', context)

@login_required
def review_response_create(request, review_id):
    """Создание ответа мастера на отзыв"""
    review = get_object_or_404(Review, pk=review_id)
    
    # Проверяем, что пользователь является мастером
    if not hasattr(request.user, 'master_profile'):
        messages.error(request, 'Только мастера могут отвечать на отзывы')
        return redirect('reviews:review_detail', pk=review_id)
    
    # Проверяем, что отзыв относится к этому мастеру
    if review.master.user != request.user:
        messages.error(request, 'Вы можете отвечать только на отзывы о вас')
        return redirect('reviews:review_detail', pk=review_id)
    
    # Проверяем, нет ли уже ответа
    if hasattr(review, 'response'):
        messages.error(request, 'На этот отзыв уже дан ответ')
        return redirect('reviews:review_detail', pk=review_id)
    
    if request.method == 'POST':
        form = ReviewResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.review = review
            response.master = review.master
            response.save()
            messages.success(request, 'Ответ успешно добавлен!')
            return redirect('reviews:review_detail', pk=review_id)
    else:
        form = ReviewResponseForm()
    
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'reviews/review_response_create.html', context)

def review_stats(request):
    """Статистика отзывов"""
    # Общая статистика
    total_reviews = Review.objects.filter(is_active=True).count()
    avg_rating = Review.objects.filter(is_active=True).aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Статистика по мастерам
    master_stats = Master.objects.filter(is_active=True).annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).filter(review_count__gt=0).order_by('-avg_rating')
    
    # Статистика по услугам
    service_stats = Service.objects.filter(is_active=True).annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).filter(review_count__gt=0).order_by('-avg_rating')
    
    # Распределение по рейтингам
    rating_distribution = Review.objects.filter(is_active=True).values('rating').annotate(
        count=Count('rating')
    ).order_by('rating')
    
    context = {
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'master_stats': master_stats,
        'service_stats': service_stats,
        'rating_distribution': rating_distribution,
    }
    return render(request, 'reviews/review_stats.html', context)
