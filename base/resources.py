from import_export import resources
from .models import Company, PlacementStatus, Student,User,PlacementApplication,PlacementApplicationResponse

class CompanyResource(resources.ModelResource):

    class Meta:
        model = Company

class UserResource(resources.ModelResource):

    class Meta:
        model = User

class StudentResource(resources.ModelResource):

    class Meta:
        model = Student

class PlacementApplicationResource(resources.ModelResource):

    class Meta:
        model = PlacementApplication

class PlacementApplicationResponseResource(resources.ModelResource):

    class Meta:
        model = PlacementApplicationResponse

class PlacementStatusResource(resources.ModelResource):

    class Meta:
        model = PlacementStatus