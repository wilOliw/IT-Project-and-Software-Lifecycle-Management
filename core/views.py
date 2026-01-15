from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Contact, News, About
from services.models import Service, Category
from masters.models import Master
from reviews.models import Review

def home(request):
    """Главная страница сайта"""
    context = {
        'featured_services': Service.objects.filter(is_active=True, is_featured=True)[:6],
        'masters': Master.objects.filter(is_active=True)[:4],
        'featured_news': News.objects.filter(is_active=True, is_featured=True)[:3],
        'recent_reviews': Review.objects.filter(is_active=True).order_by('-created_at')[:5],
        'contacts': Contact.objects.filter(is_active=True),
    }
    return render(request, 'core/home.html', context)

def about(request):
    """Страница о студии"""
    context = {
        'about_sections': About.objects.filter(is_active=True),
        'masters_count': Master.objects.filter(is_active=True).count(),
        'services_count': Service.objects.filter(is_active=True).count(),
        'reviews_count': Review.objects.filter(is_active=True).count(),
    }
    return render(request, 'core/about.html', context)

def contacts(request):
    """Страница контактов"""
    context = {
        'contacts': Contact.objects.filter(is_active=True),
    }
    return render(request, 'core/contacts.html', context)

def news_list(request):
    """Список новостей"""
    news = News.objects.filter(is_active=True)
    context = {
        'news_list': news,
    }
    return render(request, 'core/news_list.html', context)

def news_detail(request, news_id):
    """Детальная страница новости"""
    try:
        news = News.objects.get(id=news_id, is_active=True)
        context = {
            'news': news,
        }
        return render(request, 'core/news_detail.html', context)
    except News.DoesNotExist:
        messages.error(request, 'Новость не найдена')
        return redirect('news_list')

@login_required
def profile(request):
    """Личный кабинет пользователя"""
    context = {
        'user': request.user,
    }
    return render(request, 'core/profile.html', context)

def search(request):
    """Поиск по сайту"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Поиск по услугам
        services = Service.objects.filter(
            name__icontains=query, 
            is_active=True
        )[:5]
        
        # Поиск по мастерам
        masters = Master.objects.filter(
            user__first_name__icontains=query,
            is_active=True
        )[:5]
        
        # Поиск по категориям
        categories = Category.objects.filter(
            name__icontains=query
        )[:5]
        
        results = {
            'services': services,
            'masters': masters,
            'categories': categories,
        }
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'core/search.html', context)

def signup(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('core:home')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/signup.html', context)
