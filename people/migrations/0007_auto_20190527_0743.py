# Generated by Django 2.2.1 on 2019-05-27 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_facematch_human_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='missingperson',
            name='case_info_fetched',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='missingperson',
            name='current_max_age',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='missingperson',
            name='current_min_age',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='missingperson',
            name='ethnicity',
            field=models.CharField(default=None, max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='missingperson',
            name='last_fetched',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='missingperson',
            name='last_sighted',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='unidentifiedperson',
            name='case_info_fetched',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='unidentifiedperson',
            name='current_max_age',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='unidentifiedperson',
            name='current_min_age',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='unidentifiedperson',
            name='ethnicity',
            field=models.CharField(default=None, max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='unidentifiedperson',
            name='last_fetched',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='unidentifiedperson',
            name='last_sighted',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='unidentifiedperson',
            name='name',
            field=models.CharField(default=None, max_length=400, null=True),
        ),
    ]
