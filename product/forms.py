from django import forms
from .models import Product, DailyReport

class ProductForm(forms.ModelForm):
  
    class Meta:
        model = Product
        fields = ['name','unit', 'notes']
        labels = {
            'name': 'EMRI I PRODUKTIT',
            'unit': 'NJESIA',
            'notes': 'SHENIME'
        }
       
                
        
        
class SelectDataForm(forms.Form):
     year = forms.ChoiceField(
        choices=[(year, year) for year in range(2024, 2036)],
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 200px; text-align: center;'})
    )
     month = forms.ChoiceField(
        choices=[
            ('01', 'Janar'), ('02', 'Shkurt'), ('03', 'Mars'), ('04', 'Prill'),
            ('05', 'Maj'), ('06', 'Qershor'), ('07', 'Korrik'), ('08', 'Gusht'),
            ('09', 'Shtator'), ('10', 'Tetor'), ('11', 'Nentor'), ('12', 'Dhjetor')
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 200px; text-align: center;'})
    )
     labels = {
            'year': 'Viti',
            'month': 'Muaji'
        }
    
    
class DailyReportForm(forms.Form):
    action = forms.ChoiceField(choices=DailyReport.ACTION_CHOICES, label='SHITJE/BLERJE')
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label=' ', label='PRODUKTI')
    quantity = forms.DecimalField(max_digits=20, decimal_places=2, label='SASIA')
    price = forms.DecimalField(max_digits=20, decimal_places=2, label='CMIMI')
    
    
    
  
