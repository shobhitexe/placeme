# Generated by Django 3.2.6 on 2021-09-03 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_rename_prn_number_student_roll_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='roll_number',
            field=models.CharField(max_length=16, unique=True),
        ),
    ]