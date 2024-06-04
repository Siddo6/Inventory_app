from django.urls import path
from . import views


urlpatterns = [
    path('create_product', views.create_product, name='create_product'),
    path('upload_products', views.upload_products, name='upload_products'),
    path('daily_report/', views.daily_report, name='daily_report'),
    path('product_list_current_month/', views.product_list_current_month, name='product_list_current_month'),
    path('product_list/<int:year>/<int:month>/', views.product_list, name='product_list'),
    path('select_datas/', views.select_datas, name='select_datas'),
    path('product_details/<int:product_id>/<int:current_year>/<int:current_month>/', views.product_details, name='product_details'),
    path ('search_results/', views.search_results, name='search_results'),
    path('autocomplete-products/', views.autocomplete_products, name='autocomplete_products'),
    path('products/', views.list_all_products, name='list_all_products'),
    path('product_edit/<int:product_id>/', views.product_edit, name='product_edit'),
]