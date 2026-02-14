# Celery configuration for retail_core

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_core.settings')

app = Celery('retail_core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'run-demand-forecasting-every-night': {
        'task': 'ml_services.tasks.run_demand_forecasting',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight daily
    },
    'check-inventory-alerts-every-hour': {
        'task': 'alerts.tasks.check_inventory_alerts',
        'schedule': crontab(minute=0),  # Run every hour
    },
    'generate-daily-analytics-every-morning': {
        'task': 'analytics.tasks.generate_daily_analytics',
        'schedule': crontab(hour=6, minute=0),  # Run at 6 AM daily
    },
    'cleanup-old-transactions-weekly': {
        'task': 'inventory.tasks.cleanup_old_transactions',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Run Sundays at 2 AM
    },
    'process-pending-purchase-orders-every-6-hours': {
        'task': 'orders.tasks.process_pending_purchase_orders',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
