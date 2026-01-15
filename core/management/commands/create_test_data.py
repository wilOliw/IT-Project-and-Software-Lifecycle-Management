from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time
from services.models import Category, Service
from masters.models import Master, MasterService, MasterSchedule


class Command(BaseCommand):
    help = 'Создает тестовые данные для студии красоты'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        # Создаем категории услуг
        categories = self.create_categories()
        
        # Создаем услуги
        services = self.create_services(categories)
        
        # Создаем пользователей-мастеров
        masters = self.create_masters()
        
        # Связываем мастеров с услугами
        self.link_masters_services(masters, services)
        
        # Создаем расписание мастеров
        self.create_master_schedules(masters)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано:\n'
                f'- {len(categories)} категорий\n'
                f'- {len(services)} услуг\n'
                f'- {len(masters)} мастеров\n'
                f'- Расписание для всех мастеров'
            )
        )

    def create_categories(self):
        """Создает категории услуг"""
        categories_data = [
            {
                'name': 'Стрижки и укладки',
                'description': 'Профессиональные стрижки, укладки и окрашивание волос',
                'icon': 'scissors',
                'sort_order': 1
            },
            {
                'name': 'Маникюр и педикюр',
                'description': 'Классический и аппаратный маникюр, педикюр, наращивание ногтей',
                'icon': 'hand-sparkles',
                'sort_order': 2
            },
            {
                'name': 'Макияж',
                'description': 'Дневной, вечерний и свадебный макияж',
                'icon': 'paint-brush',
                'sort_order': 3
            },
            {
                'name': 'Массаж и SPA',
                'description': 'Расслабляющий массаж, SPA-процедуры для лица и тела',
                'icon': 'spa',
                'sort_order': 4
            },
            {
                'name': 'Эпиляция',
                'description': 'Восковая эпиляция, шугаринг, лазерная эпиляция',
                'icon': 'star',
                'sort_order': 5
            }
        ]
        
        categories = []
        for data in categories_data:
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Создана категория: {category.name}')
        
        return categories

    def create_services(self, categories):
        """Создает услуги"""
        services_data = [
            # Стрижки и укладки
            {
                'name': 'Женская стрижка',
                'description': 'Профессиональная стрижка с учетом формы лица и структуры волос',
                'short_description': 'Стрижка любой сложности',
                'price': 2500.00,
                'duration_minutes': 60,
                'category': categories[0],
                'is_featured': True
            },
            {
                'name': 'Мужская стрижка',
                'description': 'Классическая и современная мужская стрижка',
                'short_description': 'Стрижка + укладка',
                'price': 1800.00,
                'duration_minutes': 45,
                'category': categories[0]
            },
            {
                'name': 'Окрашивание волос',
                'description': 'Полное окрашивание с профессиональными красками',
                'short_description': 'Окрашивание любой сложности',
                'price': 4500.00,
                'duration_minutes': 120,
                'category': categories[0],
                'is_featured': True
            },
            {
                'name': 'Укладка',
                'description': 'Праздничная укладка для особых случаев',
                'short_description': 'Укладка любой сложности',
                'price': 2000.00,
                'duration_minutes': 60,
                'category': categories[0]
            },
            
            # Маникюр и педикюр
            {
                'name': 'Классический маникюр',
                'description': 'Классический маникюр с покрытием лаком',
                'short_description': 'Маникюр + лак',
                'price': 1500.00,
                'duration_minutes': 45,
                'category': categories[1]
            },
            {
                'name': 'Аппаратный маникюр',
                'description': 'Современный аппаратный маникюр с использованием фрезера',
                'short_description': 'Аппаратный маникюр + лак',
                'price': 2000.00,
                'duration_minutes': 60,
                'category': categories[1]
            },
            {
                'name': 'Наращивание ногтей',
                'description': 'Наращивание ногтей гелем или акрилом',
                'short_description': 'Наращивание + дизайн',
                'price': 3500.00,
                'duration_minutes': 90,
                'category': categories[1],
                'is_featured': True
            },
            
            # Макияж
            {
                'name': 'Дневной макияж',
                'description': 'Естественный макияж для повседневной жизни',
                'short_description': 'Дневной макияж',
                'price': 2500.00,
                'duration_minutes': 60,
                'category': categories[2]
            },
            {
                'name': 'Вечерний макияж',
                'description': 'Яркий макияж для вечерних мероприятий',
                'short_description': 'Вечерний макияж',
                'price': 3500.00,
                'duration_minutes': 90,
                'category': categories[2]
            },
            {
                'name': 'Свадебный макияж',
                'description': 'Особый макияж для самого важного дня',
                'short_description': 'Свадебный макияж',
                'price': 5000.00,
                'duration_minutes': 120,
                'category': categories[2],
                'is_featured': True
            },
            
            # Массаж и SPA
            {
                'name': 'Классический массаж',
                'description': 'Расслабляющий классический массаж всего тела',
                'short_description': 'Массаж всего тела',
                'price': 3000.00,
                'duration_minutes': 60,
                'category': categories[3]
            },
            {
                'name': 'SPA-процедура для лица',
                'description': 'Комплексный уход за лицом с масками и массажем',
                'short_description': 'SPA для лица',
                'price': 2500.00,
                'duration_minutes': 90,
                'category': categories[3]
            },
            
            # Эпиляция
            {
                'name': 'Восковая эпиляция ног',
                'description': 'Эпиляция ног горячим воском',
                'short_description': 'Эпиляция ног',
                'price': 2000.00,
                'duration_minutes': 45,
                'category': categories[4]
            },
            {
                'name': 'Шугаринг зоны бикини',
                'description': 'Эпиляция зоны бикини сахарной пастой',
                'short_description': 'Шугаринг бикини',
                'price': 1500.00,
                'duration_minutes': 30,
                'category': categories[4]
            }
        ]
        
        services = []
        for data in services_data:
            service, created = Service.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            services.append(service)
            if created:
                self.stdout.write(f'Создана услуга: {service.name}')
        
        return services

    def create_masters(self):
        """Создает мастеров"""
        masters_data = [
            {
                'username': 'anna_stylist',
                'first_name': 'Анна',
                'last_name': 'Петрова',
                'email': 'anna@studio.ru',
                'specialization': 'Парикмахер-стилист',
                'experience_years': 8,
                'bio': 'Специалист по стрижкам, окрашиванию и укладкам. Работает с волосами любой сложности.'
            },
            {
                'username': 'maria_nail',
                'first_name': 'Мария',
                'last_name': 'Иванова',
                'email': 'maria@studio.ru',
                'specialization': 'Мастер маникюра',
                'experience_years': 5,
                'bio': 'Профессиональный мастер маникюра и педикюра. Специалист по наращиванию ногтей.'
            },
            {
                'username': 'elena_makeup',
                'first_name': 'Елена',
                'last_name': 'Сидорова',
                'email': 'elena@studio.ru',
                'specialization': 'Визажист',
                'experience_years': 6,
                'bio': 'Профессиональный визажист. Специалист по дневному, вечернему и свадебному макияжу.'
            },
            {
                'username': 'irina_massage',
                'first_name': 'Ирина',
                'last_name': 'Козлова',
                'email': 'irina@studio.ru',
                'specialization': 'Массажист',
                'experience_years': 10,
                'bio': 'Опытный массажист с медицинским образованием. Специалист по классическому и лечебному массажу.'
            },
            {
                'username': 'natalia_epil',
                'first_name': 'Наталья',
                'last_name': 'Волкова',
                'email': 'natalia@studio.ru',
                'specialization': 'Мастер эпиляции',
                'experience_years': 7,
                'bio': 'Специалист по различным видам эпиляции: воск, шугаринг, лазер.'
            }
        ]
        
        masters = []
        for data in masters_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'Создан пользователь: {user.username}')
            
            master, created = Master.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': data['specialization'],
                    'experience_years': data['experience_years'],
                    'bio': data['bio']
                }
            )
            
            masters.append(master)
            if created:
                self.stdout.write(f'Создан мастер: {master.get_full_name()}')
        
        return masters

    def link_masters_services(self, masters, services):
        """Связывает мастеров с услугами"""
        # Анна - парикмахер
        master_anna = masters[0]
        hair_services = [s for s in services if s.category.name == 'Стрижки и укладки']
        for service in hair_services:
            MasterService.objects.get_or_create(
                master=master_anna,
                service=service,
                defaults={'price_modifier': 1.0, 'duration_modifier': 0}
            )
        
        # Мария - мастер маникюра
        master_maria = masters[1]
        nail_services = [s for s in services if s.category.name == 'Маникюр и педикюр']
        for service in nail_services:
            MasterService.objects.get_or_create(
                master=master_maria,
                service=service,
                defaults={'price_modifier': 1.0, 'duration_modifier': 0}
            )
        
        # Елена - визажист
        master_elena = masters[2]
        makeup_services = [s for s in services if s.category.name == 'Макияж']
        for service in makeup_services:
            MasterService.objects.get_or_create(
                master=master_elena,
                service=service,
                defaults={'price_modifier': 1.0, 'duration_modifier': 0}
            )
        
        # Ирина - массажист
        master_irina = masters[3]
        massage_services = [s for s in services if s.category.name == 'Массаж и SPA']
        for service in massage_services:
            MasterService.objects.get_or_create(
                master=master_irina,
                service=service,
                defaults={'price_modifier': 1.0, 'duration_modifier': 0}
            )
        
        # Наталья - мастер эпиляции
        master_natalia = masters[4]
        epil_services = [s for s in services if s.category.name == 'Эпиляция']
        for service in epil_services:
            MasterService.objects.get_or_create(
                master=master_natalia,
                service=service,
                defaults={'price_modifier': 1.0, 'duration_modifier': 0}
            )
        
        self.stdout.write('Мастера связаны с услугами')

    def create_master_schedules(self, masters):
        """Создает расписание для мастеров"""
        working_hours = [
            (time(9, 0), time(18, 0)),  # Пн-Пт
            (time(9, 0), time(18, 0)),  # Пн-Пт
            (time(9, 0), time(18, 0)),  # Пн-Пт
            (time(9, 0), time(18, 0)),  # Пн-Пт
            (time(9, 0), time(18, 0)),  # Пн-Пт
            (time(10, 0), time(16, 0)), # Сб
            (time(10, 0), time(16, 0)), # Вс
        ]
        
        for master in masters:
            for day_num, (start_time, end_time) in enumerate(working_hours, 1):
                # Воскресенье - выходной для всех
                is_working = day_num != 7
                
                schedule, created = MasterSchedule.objects.get_or_create(
                    master=master,
                    day_of_week=day_num,
                    defaults={
                        'start_time': start_time,
                        'end_time': end_time,
                        'is_working_day': is_working
                    }
                )
                
                if created:
                    self.stdout.write(f'Создано расписание для {master.get_full_name()} - {schedule.get_day_of_week_display()}')
        
        self.stdout.write('Расписание мастеров создано')
