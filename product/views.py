from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, DailyReport, MonthlyData
from .forms import ProductForm, DailyReportForm, SelectDataForm, ExcelUploadForm
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
import pandas as pd  
import openpyxl
from django.db import IntegrityError
from django.contrib import messages

data_cache = {}

now = datetime.now()
current_year = datetime.now().year
current_month = datetime.now().month


@login_required
def daily_report(request):
   
    selected_product_id = request.GET.get('product_filter')
    if selected_product_id:
        daily_reports = DailyReport.objects.filter(product_id=selected_product_id, created_at__year=current_year,
        created_at__month=current_month)
    else:
        daily_reports = DailyReport.objects.filter(created_at__year=current_year,
        created_at__month=current_month)
        
    if request.method == 'POST':
        form = DailyReportForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            product_name = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            price = form.cleaned_data['price']
            
            # Fetch the product instance from the database using the product name
            product = get_object_or_404(Product, name=product_name)
    
            if action == 'sale':
                 if int(quantity)  > product.actual_stock:
                    form.add_error(None, 'Po perpiqesh te shtosh shitje me sasi me te madhe se stoku aktual... Te lutem rikontrollo shifrat')
                    return render(request, 'product/daily_report.html', {'form': form, 'daily_reports': daily_reports})
            # krijon nje istance te re
            daily_report = DailyReport(
                action=action,
                product=product,
                quantity=quantity,
                price=price
            )
            current_user = request.user
            daily_report.created_by = current_user
            # e ruan reportin ne databaze
            daily_report.save()
            product.updated_at = timezone.now()
            product.save()
            
            return redirect('daily_report')  # redirect tek e njejta faqe pasi ti e ruan reportin
    else:
        form = DailyReportForm()
        
    daily_reports = DailyReport.objects.filter(created_at__year=current_year,
        created_at__month=current_month)  
   
    return render(request, 'product/daily_report.html', {'form': form, 'daily_reports': daily_reports})


#funksioni per te zgjedhur muajin per te cilin duam te shohim te dhenat
@login_required
def select_datas(request):
    if request.method == 'POST':
        form = SelectDataForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            return redirect('product_list', year=year, month=month)
    else:
        form = SelectDataForm()

    return render(request, 'product/select_datas.html', {'form': form})

#funksioni qe nxjerr produktet per muajin aktual
@login_required
def product_list_current_month (request):
    current_year = datetime.now().year
    current_month = datetime.now().month
     # filtron reportet per muajin aktual
    daily_reports = DailyReport.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month
    )

    # nxjerr listen e prdukteve per te cilat ka reporte, pa duplikate
    products = Product.objects.filter(id__in=daily_reports.values_list('product', flat=True))
    
    for product in products:
        product.celja_quantity = calculate_celja(product.id, current_year, current_month)
        total_cost = 0
        total_revenue = 0
        buys = 0
        sales = 0
        # iteron te cdo report per cdo produkt qe te llogariten shitje e blerje 
        for report in daily_reports.filter(product=product):
                if report.action == 'buy':
                        total_cost += report.cost
                        buys += report.quantity
                elif report.action == 'sale':
                        total_revenue += report.revenue
                        sales += report.quantity

        product.total_cost_per_product = total_cost
        product.total_revenue_per_product = total_revenue
        product.buys = buys
        product.sales = sales
        product.total_stock = product.celja_quantity + product.buys
        product.actual_stock = product.total_stock - product.sales
        product.save()

       
    return render(request, 'product/product_list_current_month.html', {
        'products': products,
        'current_year': current_year,
        'current_month': current_month,
    })

#funksioni qe nxjerr te dhenat per muajt e kaluar qe i zgjodhem me perpara te select_datas
@login_required
def product_list(request, year=None, month=None):
    # merr muajin dhe vitin
    
    year = current_year if year is None else year
    month = current_month if month is None else month
    
    # filtro DailyReports per muajin e zgjedhur
    daily_reports = DailyReport.objects.filter(
        created_at__year=year,
        created_at__month=month
    )

    # nga filtrimi me siper nxjerr nje liste me produktet qe jane tek ato reporte, pa vlera duplikate
    products = Product.objects.filter(id__in=daily_reports.values_list('product', flat=True))

    for product in products:
        #logic here        

        product.total_cost_per_product = total_cost
        product.total_revenue_per_product = total_revenue
        product.buys = buys
        product.sales = sales
        product.total_stock = product.celja_quantity + product.buys
        product.actual_stock = product.celja_quantity + product.buys - product.sales
        product.save()
           
            
    return render(request, 'product/product_list.html', {
            'products': products,
            'year': year,
            'month': month,
            'current_year': current_year, 
            'current_month': current_month})
   
#funksioni per te hedhur nje produkt te ri ne sistem
@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)  # Don't save yet
            product.created_by = request.user  # Set the created_by field
            product.created_at = timezone.now() 
            product.save()  # Now save the product with the created_by user
            return redirect('index')
    else:
        form = ProductForm()

    return render(request, 'product/create_product.html', {'form': form})

#funksioni qe hap te dhenat per cdo produkt

def product_details(request, product_id, current_year, current_month):
    
    product = get_object_or_404(Product, pk=product_id)
    
    reports = product.get_all_reports()
    
    return render(request, 'product/product_details.html', {'product': product, 'reports': reports, 'current_year':current_year, 'current_month':current_month})


@login_required
def search_results (request):
    query = request.GET.get('q')
   
    if query:
        results = Product.objects.filter(Q(name__icontains=query))
        if results:
            for prod in results:
                reports = prod.get_all_reports()
            return render(request, 'product/search_results.html', {
                'results': results,
                'query': query,
                'reports':reports,
            })
        else:
             return render(request, 'product/search_results.html', {
            'results': results,
            'query': query, 
        })

    else:
        results=Product.objects.none()
        
        return render(request, 'product/search_results.html', {
            'results': results,
            'query': query, 
        })


def calculate_celja(product_id, year, month):

    product = Product.objects.get(pk=product_id)
    
    # Calculate the previous month
    if month == 1:  # If the current month is January
        previous_month = 12  # Set the previous month to December
        previous_year = year - 1  # Set the previous year to the previous year
    else:
        previous_month = month - 1  # Set the previous month to the previous month
        previous_year = year  # Set the previous year to the current year

    if month == product.product_created_at.month and year == product.product_created_at.year:
        product.celja_quantity = 0
    else:
        total_stock, sales = get_total_stock_and_sales(product_id, previous_year, previous_month)    
        product.celja_quantity = total_stock - sales

    product.save()
    return product.celja_quantity


def get_total_stock_and_sales(product_id, year, month):
    product = get_object_or_404(Product, pk=product_id)
    daily_reports = DailyReport.objects.filter(
        product=product,
        created_at__year=year,
        created_at__month=month
    )
    
    buys = 0
    sales = 0

    for report in daily_reports:
        if report.action == 'buy':
            buys += report.quantity
        else:
            sales += report.quantity

    if month == product.product_created_at.month and year == product.product_created_at.year:
        product.celja_quantity = 0
    else:
        product.celja_quantity = calculate_celja(product_id, year, month)

    product.buys = buys
    product.total_stock = buys + product.celja_quantity
    product.sales = sales
    product.actual_stock = product.total_stock - sales

    return product.total_stock, product.sales


def autocomplete_products(request):
    if 'term' in request.GET:
        qs = Product.objects.filter(name__icontains=request.GET.get('term'))
        products = list(qs.values_list('name', flat=True))
        return JsonResponse(products, safe=False)
    return JsonResponse([], safe=False)


def upload_products(request):
     if request.method == 'POST':
        excel_form = ExcelUploadForm(request.POST, request.FILES)
        if excel_form.is_valid():
            excel_file = request.FILES['excel_file']
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            duplicate_products = []

            for row in sheet.iter_rows(min_row=2, values_only=True):
                name = row[0]  # Assuming first column is the product name
                unit = row[1] if len(row) > 1 and row[1] is not None else ''  # Ensure unit is a non-null string
                notes = row[2] if len(row) > 2 and row[2] is not None else ''  # Ensure notes is a non-null string

                if name:  # Check if the name is present
                    try:
                        Product.objects.create(name=name, unit=unit, notes=notes)
                    except IntegrityError:
                        duplicate_products.append(name)
                        continue

            wb.close()

            if duplicate_products:
                messages.error(request, f"Products with the following names already exist: {', '.join(duplicate_products)}")

            return redirect('index')  # Redirect after successful upload or if there are duplicates
     else:
        excel_form = ExcelUploadForm()
    
     return render(request, 'product/upload_products.html', {'excel_form': excel_form})
 

def list_all_products(request):
    products = Product.objects.all()
    return render(request, 'product/list_all_products.html', {'products': products})
    
def product_edit(request, product_id):
   
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            product.last_modified_by = request.user
            return redirect('product_details', product_id=product.id, current_year=current_year, current_month=current_month)  # Redirect to product details
    else:
        form = ProductForm(instance=product)

    return render(request, 'product/product_edit.html', {'form': form})


def save_totals(year, month):
    
     # filtron reportet per muajin e zgjedhur
    daily_reports = DailyReport.objects.filter(
        created_at__year=year,
        created_at__month=month
    )

    # nxjerr listen e prdukteve per te cilat ka reporte, pa duplikate
    products = Product.objects.filter(id__in=daily_reports.values_list('product', flat=True))
    
    # Initialize the year and month in the cache if not already present
    if year not in data_cache:
        data_cache[year] = {}
    if month not in data_cache[year]:
        data_cache[year][month] = {}

    for product in products:
        product.celja_quantity = calculate_celja(product.id, year, month)
        total_cost = 0
        total_revenue = 0
        buys = 0
        sales = 0
        # iteron te cdo report per cdo produkt qe te llogariten shitje e blerje 
        for report in daily_reports.filter(product=product):
                if report.action == 'buy':
                        total_cost += report.cost
                        buys += report.quantity
                elif report.action == 'sale':
                        total_revenue += report.revenue
                        sales += report.quantity

        product.total_cost_per_product = total_cost
        product.total_revenue_per_product = total_revenue
        product.buys = buys
        product.sales = sales
        product.total_stock = product.celja_quantity + product.buys
        
        data_cache[year][month][product.id] = {
            'celja_quantity': product.celja_quantity,
            'total_stock': product.total_stock,
            'total_sales': product.sales,
            'total_revenue_per_product': product.total_revenue_per_product,
            'total_cost_per_product': product.total_cost_per_product
        }
        
    return data_cache[year][month]

def get_data(year, month, product_id, property):
    return data_cache.get(year, {}).get(month, {}).get(product_id, {}).get(property)