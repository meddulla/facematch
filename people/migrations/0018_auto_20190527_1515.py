# Generated by Django 2.2.1 on 2019-05-27 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0017_facematch_human_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='missingface',
            name='in_collection',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='unidentifiedface',
            name='in_collection',
            field=models.BooleanField(default=True),
        ),
    ]
