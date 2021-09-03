# Generated by Django 3.2.6 on 2021-09-02 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_placementapplicationresponsefiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='placementapplicationresponsefiles',
            name='files',
        ),
        migrations.AddField(
            model_name='placementapplicationresponsefiles',
            name='file_uploaded',
            field=models.FileField(default=1, upload_to=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='placementapplicationresponsefiles',
            name='label',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]