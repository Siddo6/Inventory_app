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
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2})  # Adjust the size of the notes field
        }
         
class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()      
        
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
    product = forms.CharField(label='PRODUKTI', widget=forms.TextInput(attrs={'placeholder': 'Search for a product...', 'id': 'product-search'}))
    quantity = forms.DecimalField(max_digits=20, decimal_places=2, label='SASIA')
    price = forms.DecimalField(max_digits=20, decimal_places=2, label='CMIMI')
    
    
    
  
