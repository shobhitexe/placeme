# forms.py
from django import forms
from .models import Company,Student
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Layout, Row, Column,Field)
  
class AddCompanyForm(forms.ModelForm):
  
    class Meta:
        model = Company
        fields = "__all__"

class StudentDetailsForm(forms.ModelForm):
  
    class Meta:
        model = Student
        fields = "__all__"


