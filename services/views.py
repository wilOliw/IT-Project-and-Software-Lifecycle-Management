from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Service, Category

def service_list(request):
    """Список всех услуг"""
    services = Service.objects.filter(is_active=True)
    
    # Фильтрация по категории
    category_id = request.GET.get('category')
    if category_id:
        services = services.filter(category_id=category_id)
    
    # Поиск по названию
    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Сортировка
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price':
        services = services.order_by('price')
    elif sort_by == 'price_desc':
        services = services.order_by('-price')
    elif sort_by == 'duration':
        services = services.order_by('duration_minutes')
    else:
        services = services.order_by('sort_order', 'name')
    
    # Пагинация
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'selected_category': category_id,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'services/service_list.html', context)

def service_detail(request, pk):
    """Детальная страница услуги"""
    service = get_object_or_404(Service, pk=pk, is_active=True)
    
    # Похожие услуги
    related_services = Service.objects.filter(
        category=service.category,
        is_active=True
    ).exclude(pk=pk)[:4]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'services/service_detail.html', context)

def category_detail(request, pk):
    """Детальная страница категории"""
    category = get_object_or_404(Category, pk=pk, is_active=True)
    services = Service.objects.filter(category=category, is_active=True)
    
    # Пагинация
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'services': page_obj,
    }
    return render(request, 'services/category_detail.html', context)

def price_list(request):
    """Прайс-лист всех услуг"""
    categories = Category.objects.filter(is_active=True).prefetch_related('services')
    
    context = {
        'categories': categories,
    }
    return render(request, 'services/price_list.html', context)
