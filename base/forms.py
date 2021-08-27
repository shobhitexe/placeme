# forms.py
from django import forms
from .models import Company
  
class AddCompanyForm(forms.ModelForm):
  
    class Meta:
        model = Company
        fields = ['name', 'description', 'logo', 'is_dream' , 'starting_salary']