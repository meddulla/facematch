# Generated by Django 2.2.1 on 2019-05-27 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_auto_20190527_0743'),
    ]

    operations = [
        migrations.AddField(
            model_name='missingperson',
            name='has_case_info',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='unidentifiedperson',
            name='has_case_info',
            field=models.BooleanField(default=False),
        ),
    ]