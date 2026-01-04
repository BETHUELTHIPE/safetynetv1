import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpfcrimereportingsystem.settings')

# Create the Celery app
app = Celery('cpfcrimereportingsystem')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery Beat schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    # Send monthly crime report on the 1st day of each month at 6:00 AM
    'send-monthly-crime-report': {
        'task': 'reports.tasks.send_monthly_report_email',
        'schedule': crontab(day_of_month='1', hour='6', minute='0'),
        'args': (),
    },
    
    # For testing purposes - uncomment to run every minute
    # 'test-crime-report': {
    #     'task': 'reports.tasks.generate_monthly_crime_report',
    #     'schedule': 60,  # every minute
    #     'args': (),
    # },
}

@app.task(bind=True)
def debug_task(self):
    """Task to help with debugging."""
    print(f'Request: {self.request!r}')
