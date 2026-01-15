from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Portfolio
from masters.models import Master
from services.models import Service

def portfolio_list(request):
    """Список всех работ в портфолио"""
    portfolio_works = Portfolio.objects.filter(is_active=True)
    
    # Фильтрация по мастеру
    master_id = request.GET.get('master')
    if master_id:
        portfolio_works = portfolio_works.filter(master_id=master_id)
    
    # Фильтрация по услуге
    service_id = request.GET.get('service')
    if service_id:
        portfolio_works = portfolio_works.filter(service_id=service_id)
    
    # Поиск по названию
    search_query = request.GET.get('search')
    if search_query:
        portfolio_works = portfolio_works.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Сортировка
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'oldest':
        portfolio_works = portfolio_works.order_by('created_at')
    elif sort_by == 'title':
        portfolio_works = portfolio_works.order_by('title')
    else:
        portfolio_works = portfolio_works.order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(portfolio_works, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'portfolio_works': page_obj,
        'masters': Master.objects.filter(is_active=True),
        'services': Service.objects.filter(is_active=True),
        'selected_master': master_id,
        'selected_service': service_id,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'portfolio/portfolio_list.html', context)

def portfolio_detail(request, pk):
    """Детальная страница работы в портфолио"""
    portfolio_work = get_object_or_404(Portfolio, pk=pk, is_active=True)
    
    # Похожие работы того же мастера
    related_works = Portfolio.objects.filter(
        master=portfolio_work.master,
        is_active=True
    ).exclude(pk=pk)[:4]
    
    # Работы по той же услуге
    similar_service_works = Portfolio.objects.filter(
        service=portfolio_work.service,
        is_active=True
    ).exclude(pk=pk)[:4]
    
    context = {
        'portfolio_work': portfolio_work,
        'related_works': related_works,
        'similar_service_works': similar_service_works,
    }
    return render(request, 'portfolio/portfolio_detail.html', context)

def master_portfolio(request, master_id):
    """Портфолио конкретного мастера"""
    master = get_object_or_404(Master, pk=master_id, is_active=True)
    portfolio_works = Portfolio.objects.filter(master=master, is_active=True)
    
    # Фильтрация по услуге
    service_id = request.GET.get('service')
    if service_id:
        portfolio_works = portfolio_works.filter(service_id=service_id)
    
    # Пагинация
    paginator = Paginator(portfolio_works, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'master': master,
        'portfolio_works': page_obj,
        'services': Service.objects.filter(is_active=True),
        'selected_service': service_id,
    }
    return render(request, 'portfolio/master_portfolio.html', context)

def service_portfolio(request, service_id):
    """Портфолио по конкретной услуге"""
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    portfolio_works = Portfolio.objects.filter(service=service, is_active=True)
    
    # Фильтрация по мастеру
    master_id = request.GET.get('master')
    if master_id:
        portfolio_works = portfolio_works.filter(master_id=master_id)
    
    # Пагинация
    paginator = Paginator(portfolio_works, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'service': service,
        'portfolio_works': page_obj,
        'masters': Master.objects.filter(is_active=True),
        'selected_master': master_id,
    }
    return render(request, 'portfolio/service_portfolio.html', context)

def featured_portfolio(request):
    """Рекомендуемые работы в портфолио"""
    featured_works = Portfolio.objects.filter(is_active=True, is_featured=True)
    
    context = {
        'featured_works': featured_works,
    }
    return render(request, 'portfolio/featured_portfolio.html', context)
