from django.contrib import admin
from .models import Company,Student,CompanyApplicationForm

# Register your models here.

admin.site.register(Company)
admin.site.register(Student)
admin.site.register(CompanyApplicationForm)