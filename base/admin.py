from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseAdmin
from .models import Company,Student,PlacementApplication,PlacementApplicationResponse,PlacementApplicationResponseFiles,PlacementStatus
from import_export.admin import ImportExportModelAdmin
from .resources import UserResource

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
class PlacementStatusAdmin(ImportExportModelAdmin):
    pass

class UserAdmin(BaseAdmin, ImportExportModelAdmin):
    resource_class = UserResource

admin.site.unregister(User)
admin.site.register(User, UserAdmin)