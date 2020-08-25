import os

from celery import Celery


# Задаем переменную окружения,
# содержащую название файла настроек нашего проекта.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a_male_3_myshop.settings')

# Создаем экземлпяр приложения.
app = Celery('a_male_3_myshop')

# загружаем конфигурацию настроек нашего проекта.
app.config_from_object('django.conf:settings', namespace='CELERY')
# вызываем процесс поиска и загрузки асинхронных задач по нашему проекту
# (из файлов tasks.py каждого из приложенией добавленных в INSTALLED_APPS)
app.autodiscover_tasks()
