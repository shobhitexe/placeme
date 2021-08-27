from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# Create your models here.

image_storage = FileSystemStorage(
    # Physical file location ROOT
    location=u'{0}/companies/'.format(settings.MEDIA_ROOT),
    # Url for file
    base_url=u'{0}companies/'.format(settings.MEDIA_URL),
)

def image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/companies/<filename>
    return u'{0}'.format(filename)

class Company(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=500,blank=True)
    logo = models.ImageField(blank = True,upload_to=image_directory_path, storage=image_storage)
    is_dream = models.BooleanField(blank = False)
    starting_salary = models.IntegerField(blank=False)
    
    class Meta:
        verbose_name_plural = "Company"
