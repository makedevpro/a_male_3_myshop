import os

from celery import Celery


# Задаем переменную окружения,
# содержащую название файла настроек нашего проекта.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

# Создаем экземлпяр приложения.
app = Celery('myshop')

# загружаем конфигурацию настроек нашего проекта.
app.config_from_object('django.cong:settings', namespace='CELERY')
# вызываем процесс поиска и загрузки асинхронных задач по нашему проекту
# (из файлов tasks.py каждого из приложенией добавленных в INSTALLED_APPS)
app.autodiscover_tasks()
