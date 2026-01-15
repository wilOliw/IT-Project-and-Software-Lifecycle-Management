from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Master, MasterService

def master_list(request):
    """Список всех мастеров"""
    masters = Master.objects.filter(is_active=True)
    
    # Фильтрация по специализации
    specialization = request.GET.get('specialization')
    if specialization:
        masters = masters.filter(specialization__icontains=specialization)
    
    # Поиск по имени
    search_query = request.GET.get('search')
    if search_query:
        masters = masters.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )
    
    # Сортировка
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'experience':
        masters = masters.order_by('-experience_years')
    elif sort_by == 'name':
        masters = masters.order_by('user__first_name')
    else:
        masters = masters.order_by('sort_order', 'user__first_name')
    
    # Пагинация
    paginator = Paginator(masters, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получение уникальных специализаций для фильтра
    specializations = Master.objects.filter(
        is_active=True
    ).values_list('specialization', flat=True).distinct()
    
    context = {
        'masters': page_obj,
        'specializations': specializations,
        'selected_specialization': specialization,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'masters/master_list.html', context)

def master_detail(request, pk):
    """Детальная страница мастера"""
    master = get_object_or_404(Master, pk=pk, is_active=True)
    
    # Услуги мастера
    master_services = MasterService.objects.filter(
        master=master, 
        is_active=True
    ).select_related('service')
    
    # Расписание мастера
    schedule = master.schedule.all().order_by('day_of_week')
    
    # Другие мастера той же специализации
    related_masters = Master.objects.filter(
        specialization=master.specialization,
        is_active=True
    ).exclude(pk=pk)[:3]
    
    context = {
        'master': master,
        'master_services': master_services,
        'schedule': schedule,
        'related_masters': related_masters,
    }
    return render(request, 'masters/master_detail.html', context)

def master_by_service(request, service_id):
    """Мастера, предоставляющие конкретную услугу"""
    from services.models import Service
    
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    master_services = MasterService.objects.filter(
        service=service,
        is_active=True
    ).select_related('master')
    
    context = {
        'service': service,
        'master_services': master_services,
    }
    return render(request, 'masters/master_by_service.html', context)
