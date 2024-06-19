from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

current_year = datetime.now().year
current_month = datetime.now().month


class DailyReport (models.Model):
    
    ACTION_CHOICES = [
        ('buy', 'BLERJE'),
        ('sale', 'SHITJE'),
    ]
    
    action = models.CharField(max_length=4, choices=ACTION_CHOICES, default = 'buy')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='daily_reports')
    quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    revenue = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    cost= models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    
    def __str__(self):
            return f"{self.product} - {self.action}"
        
    def save(self, *args, **kwargs):
        if self.action == 'sale':
            self.revenue = self.quantity * self.price      
        else:
            self.cost = self.quantity * self.price

        super().save(*args, **kwargs)
        

class Product (models.Model):
    
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('L', 'Liter'),
        ('ml', 'Milliliter'),
        ('pcs', 'Cope'),
       
    ]
    
    
    name=models.CharField(max_length=255, unique=True)
    celja_quantity = models.DecimalField(default=0, decimal_places=2, max_digits=20, editable=False) #celja qe do llogaritet muaj per muaj 
    actual_stock = models.DecimalField(default=0, decimal_places=2, max_digits=20) #stoku aktual per muajin aktual
    total_stock = models.DecimalField(default=0, decimal_places=2, max_digits=20) #stoku total per muajin e zgjedhur
    product_created_at = models.DateTimeField(auto_now_add=True) #kur eshte hedhur produkti ne sistem 
    updated_at = models.DateTimeField(null=True, blank=True) #kur eshte bere ndonje ndryshim ne produkt (hedhje report, modifikim etj)
    notes = models.TextField (blank=True)  #momentalisht nuk jan editable 
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='created_products') 
    last_modified_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    search_vector = SearchVectorField(null=True, editable = False)
    total_cost_per_product = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True) #sa eshte shpenzuar per blerje per produktin e zgjedhur ne muajin e gjedhur
    total_revenue_per_product = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)#sa eshte gjeneruar fitim per produktin e zgjedhur ne muajin e gjedhur
    buys = models.DecimalField(max_digits=20, decimal_places=2, default=0) #sasia e blerjeve per produktin ne muajin e zgjedhur
    sales = models.DecimalField(max_digits=20, decimal_places=2, default=0)#sasia e shitjeve per produktin ne muajin e zgjedhur
        
    def get_monthly_reports(self, year, month):
        return DailyReport.objects.filter(
            product=self,
            created_at__year=year,
            created_at__month=month
        ).order_by('-created_at')
        
    def get_all_reports(self):
        return DailyReport.objects.filter(
            product=self
        ).order_by('-created_at')

        
    def update_stock_quantities(self, year, month):
        celja_quantity = self.celja_quantity
        total_stock = celja_quantity
        actual_stock = total_stock
        buys = 0
        sales = 0
        
        daily_reports = DailyReport.objects.filter(
            product_id=self.pk,
            created_at__year=year,
            created_at__month=month
        )  
        
        for report in daily_reports:
            if report.action == 'buy':
                buys += report.quantity
                total_stock += report.quantity
                actual_stock += report.quantity
            elif report.action == 'sale':
                sales += report.quantity
                actual_stock -= report.quantity
        
        # Update the product instance with the calculated values
        self.total_stock = total_stock
        self.actual_stock = actual_stock
        self.buys = buys
        self.sales = sales
        self.save()  # Save the changes to the database

    @receiver(post_save, sender=DailyReport)
    def update_product_stock(sender, instance, **kwargs):
            # When a new DailyReport is created or modified, update the related product's stock quantities
            current_year = datetime.now().year
            current_month = datetime.now().month
            instance.product.update_stock_quantities(current_year, current_month)
    
    def __str__(self):
        return self.name


class MonthlyData(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    previous_total_stock = models.IntegerField()
    previous_sales = models.IntegerField()
    celja = models.IntegerField()
    previous_month_celja = models.IntegerField(default=0)

    class Meta:
        unique_together = ['product', 'year', 'month']