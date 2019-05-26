# Generated by Django 2.2.1 on 2019-05-26 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='facematch',
            options={'ordering': ('-id',), 'verbose_name_plural': 'Face Matches'},
        ),
        migrations.AddField(
            model_name='missingface',
            name='is_face',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='missingface',
            name='last_searched',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='missingface',
            name='searched',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='unidentifiedface',
            name='is_face',
            field=models.BooleanField(default=True),
        ),
    ]
