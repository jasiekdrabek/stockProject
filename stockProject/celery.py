from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# ustawienie domyślnego modułu ustawień Django dla Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockProject.settings')

app = Celery('stockProject')

# Konfiguracja Celery, używając ustawień Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatyczne odkrywanie zadań (tasks.py w aplikacjach Django)
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

'''
app.conf.beat_schedule = {
    'execute-transactions-every-minute': {
        'task': 'stockApp.tasks.execute_transactions',
        'schedule': crontab(minute='*/1'),  # co minutę
    },
}
'''

app.conf.beat_schedule = {
    'schedule_transactions': {
        'task': 'stockApp.tasks.schedule_transactions',
        'schedule': 30.0,  # co 30 s
    }
}
'''
    'update_stock_rates': {
        'task': 'stockApp.tasks.update_stock_rates',
        'schedule': 10.0,  # co 10 sekund
    },
'''
