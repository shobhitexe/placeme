from django.contrib import admin
from .models import Company,Student,PlacementApplication,PlacementApplicationResponse,PlacementApplicationResponseFiles

# Register your models here.

admin.site.register(Company)
admin.site.register(Student)
admin.site.register(PlacementApplication)
admin.site.register(PlacementApplicationResponse)
admin.site.register(PlacementApplicationResponseFiles)