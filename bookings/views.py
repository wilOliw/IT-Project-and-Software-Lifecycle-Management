from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Appointment, TimeSlot
from .forms import AppointmentForm, AppointmentFilterForm
from services.models import Service
from masters.models import Master

@login_required
def appointment_create(request):
    """Создание новой записи"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            
            # Если мастер не выбран, назначаем доступного
            if not appointment.master:
                appointment.master = _get_available_master(
                    appointment.service, 
                    appointment.appointment_date, 
                    appointment.start_time
                )
            
            # Сохраняем запись (end_time будет рассчитан автоматически в save())
            appointment.save()
            messages.success(request, 'Запись успешно создана!')
            return redirect('bookings:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm()
    
    context = {
        'form': form,
        'services': Service.objects.filter(is_active=True),
        'masters': Master.objects.filter(is_active=True),
    }
    return render(request, 'bookings/appointment_create.html', context)

@login_required
def appointment_list(request):
    """Список записей пользователя"""
    appointments = Appointment.objects.filter(client=request.user)
    
    # Фильтрация
    filter_form = AppointmentFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('status'):
            appointments = appointments.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data.get('date_from'):
            appointments = appointments.filter(appointment_date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data.get('date_to'):
            appointments = appointments.filter(appointment_date__lte=filter_form.cleaned_data['date_to'])
        if filter_form.cleaned_data.get('master'):
            appointments = appointments.filter(master=filter_form.cleaned_data['master'])
        if filter_form.cleaned_data.get('service'):
            appointments = appointments.filter(service=filter_form.cleaned_data['service'])
    
    # Пагинация
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'appointments': page_obj,
        'filter_form': filter_form,
    }
    return render(request, 'bookings/appointment_list.html', context)

@login_required
def appointment_detail(request, pk):
    """Детальная страница записи"""
    appointment = get_object_or_404(Appointment, pk=pk, client=request.user)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'bookings/appointment_detail.html', context)

@login_required
def appointment_edit(request, pk):
    """Редактирование записи"""
    appointment = get_object_or_404(Appointment, pk=pk, client=request.user)
    
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, 'Нельзя редактировать завершенную или отмененную запись')
        return redirect('bookings:appointment_detail', pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Запись успешно обновлена!')
            return redirect('bookings:appointment_detail', pk=pk)
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'bookings/appointment_edit.html', context)

@login_required
def appointment_cancel(request, pk):
    """Отмена записи"""
    appointment = get_object_or_404(Appointment, pk=pk, client=request.user)
    
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, 'Нельзя отменить завершенную или уже отмененную запись')
        return redirect('bookings:appointment_detail', pk=pk)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Запись успешно отменена!')
        return redirect('bookings:appointment_list')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'bookings/appointment_cancel.html', context)

def available_times(request):
    """Получение доступных временных слотов"""
    master_id = request.GET.get('master')
    service_id = request.GET.get('service')
    date = request.GET.get('date')
    
    if not all([master_id, service_id, date]):
        return JsonResponse({'times': []})
    
    try:
        master = Master.objects.get(pk=master_id)
        service = Service.objects.get(pk=service_id)
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
    except (Master.DoesNotExist, Service.DoesNotExist, ValueError):
        return JsonResponse({'times': []})
    
    # Получаем доступные временные слоты
    available_times_list = _get_available_times(master, service, appointment_date)
    
    # Преобразуем время в строки для JSON
    times_str = [time.strftime('%H:%M') for time in available_times_list]
    
    return JsonResponse({'times': times_str})

def _get_available_master(service, date, start_time):
    """Получает доступного мастера для услуги"""
    # Ищем мастера, который предоставляет эту услугу
    available_masters = Master.objects.filter(
        services=service,
        is_active=True
    )
    
    for master in available_masters:
        if not _is_time_conflicting(master, date, start_time, service.duration_minutes):
            return master
    
    return available_masters.first()

def _get_available_times(master, service, date):
    """Получает доступные временные слоты для мастера и услуги"""
    # Время работы студии
    start_hour = 9
    end_hour = 21
    slot_duration = 30  # 30-минутные слоты
    
    available_times = []
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:
            time_slot = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
            
            # Проверяем, доступно ли время
            if not _is_time_conflicting(master, date, time_slot, service.duration_minutes):
                available_times.append(time_slot)
    
    return available_times

def _is_time_conflicting(master, date, start_time, duration_minutes):
    """Проверяет, есть ли конфликт времени"""
    if not duration_minutes:
        duration_minutes = 30  # По умолчанию 30 минут
    
    start_datetime = datetime.combine(date, start_time)
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    end_time = end_datetime.time()
    
    # Проверяем существующие записи
    conflicting_appointments = Appointment.objects.filter(
        master=master,
        appointment_date=date,
        status__in=['pending', 'confirmed'],
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    
    return conflicting_appointments.exists()

# Административные представления
@login_required
def admin_appointment_list(request):
    """Список всех записей для администраторов"""
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('core:home')
    
    appointments = Appointment.objects.all().select_related('client', 'master', 'service')
    
    # Фильтрация
    filter_form = AppointmentFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('status'):
            appointments = appointments.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data.get('date_from'):
            appointments = appointments.filter(appointment_date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data.get('date_to'):
            appointments = appointments.filter(appointment_date__lte=filter_form.cleaned_data['date_to'])
        if filter_form.cleaned_data.get('master'):
            appointments = appointments.filter(master=filter_form.cleaned_data['master'])
        if filter_form.cleaned_data.get('service'):
            appointments = appointments.filter(service=filter_form.cleaned_data['service'])
    
    # Пагинация
    paginator = Paginator(appointments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'appointments': page_obj,
        'filter_form': filter_form,
    }
    return render(request, 'bookings/admin_appointment_list.html', context)

@login_required
def admin_appointment_edit(request, pk):
    """Редактирование записи администратором"""
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('core:home')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Запись успешно обновлена!')
            return redirect('bookings:admin_appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'bookings/admin_appointment_edit.html', context)
