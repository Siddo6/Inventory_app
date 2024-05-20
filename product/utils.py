from django.utils import timezone
from .models import MonthlyData
from .models import Product
from .views import get_total_stock_and_sales, calculate_celja


def calculate_and_store_monthly_data():
    now = timezone.now()
    if now.day == 1:  # Check if it's the first day of the month
        current_month = now.month
        current_year = now.year
        previous_month = current_month - 1 if current_month > 1 else 12
        previous_year = current_year if previous_month != 12 else current_year - 1

        for product in Product.objects.all():
            # Calculate and store celja for the current month
            celja = calculate_celja(product.pk, current_year, current_month)

            # Calculate and store total stock and sales for the previous month
            previous_total_stock, previous_sales = get_total_stock_and_sales(product.pk, previous_year, previous_month)

            # Store the data in MonthlyData model
            MonthlyData.objects.update_or_create(
                product=product,
                year=current_year,
                month=current_month,
                defaults={
                    'celja': celja,
                    'previous_total_stock': previous_total_stock,
                    'previous_sales': previous_sales,
                }
            )
    else:
        print("Not the first day of the month. Skipping monthly update.")
