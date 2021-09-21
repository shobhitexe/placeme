from django.contrib import admin
from django.contrib.auth.models import User
from .models import Company,Student,PlacementApplication,PlacementApplicationResponse,PlacementApplicationResponseFiles,PlacementStatus
from import_export.admin import ImportExportModelAdmin

# Register your models here.

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    pass

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    pass

@admin.register(PlacementApplication)
class PlacementApplicationAdmin(ImportExportModelAdmin):
    pass

@admin.register(PlacementApplicationResponse)
class PlacementApplicationResponseAdmin(ImportExportModelAdmin):
    pass

@admin.register(PlacementApplicationResponseFiles)
class PlacementApplicationResponseFilesAdmin(ImportExportModelAdmin):
    pass

@admin.register(PlacementStatus)
class PlacementStatus(ImportExportModelAdmin):
    pass
