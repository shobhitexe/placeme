# forms.py
from django import forms
from .models import Company,Student
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Layout, Row, Column,Field)
  
class AddCompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = "__all__"
        labels ={'is_dream': 'Dream Company','starting_salary':'Starting Salary','day':'Day'}

class StudentDetailsForm(forms.ModelForm):
  
    class Meta:
        model = Student
        exclude = ['user']
        labels = {
            'roll_number': 'Roll Number',
            'contact_number': 'Contact Number',
            'college_email_id' : 'College Email ID',
            'class10_board' : 'Class 10 Board',
            'class10_school' : 'Class 10 School Name',
            'class10_percentage' : 'Class 10 Percentage',
            'class12_board' : 'Class 12 Board/ Diploma',
            'class12_college' : 'Class 12 College Name',
            'class12_percentage' : 'Class 12 Percentage',
            'undergraduate_stream' : 'Undergraduate Stream',
            'undergraduate_specialization' : 'Undergraduate Specialization',
            'sem1_sgpi' : 'Sem 1 SGPI',
            'sem2_sgpi' : 'Sem 2 SGPI',
            'sem3_sgpi' : 'Sem 3 SGPI',
            'sem4_sgpi' : 'Sem 4 SGPI',
            'sem5_sgpi' : 'Sem 5 SGPI',
            'sem6_sgpi' : 'Sem 6 SGPI',
            'sem7_sgpi' : 'Sem 7 SGPI',
            'sem8_sgpi' : 'Sem 8 SGPI',
            'cgpa' : 'CGPA',
            'live_kt' : 'Live KT',
            'year_drop' : 'Year Drop',
            'education_gap' : 'Education Gap',
            'year_joined' : 'Year Joined',
            'expected_grad_year' : 'Graduation Year',
        }

class CompanyApplicationForm(forms.Form):
    pass

    def set_initial(self,responses,*args, **kwargs):
        for key in responses.keys():
            self.fields[key].initial = responses[key]