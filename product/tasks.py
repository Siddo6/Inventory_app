from celery import shared_task
from django.utils import timezone
from .utils import calculate_and_store_monthly_data

@shared_task
def calculate_and_store_monthly_data_task():
    now = timezone.now()
    if now.day == 1:  # Check if it's the first day of the month
        calculate_and_store_monthly_data()