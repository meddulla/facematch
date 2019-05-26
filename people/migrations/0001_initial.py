# Generated by Django 2.2.1 on 2019-05-26 00:46

from django.db import migrations, models
import django.db.models.deletion
import facematch.storage_backends


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MissingPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=400, null=True)),
                ('code', models.CharField(default=None, max_length=400, null=True, unique=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')], default='U', max_length=2)),
                ('photo', models.ImageField(default=None, null=True, storage=facematch.storage_backends.MissingStorage(), upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='UnidentifiedPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=None, max_length=400, null=True, unique=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')], default='U', max_length=2)),
                ('photo', models.ImageField(default=None, null=True, storage=facematch.storage_backends.UnidentifiedStorage(), upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='UnidentifiedFace',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('bounding_box', models.TextField(default=None, null=True)),
                ('photo', models.ImageField(default=None, null=True, storage=facematch.storage_backends.UnidentifiedStorage(), upload_to='')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.UnidentifiedPerson')),
            ],
        ),
        migrations.CreateModel(
            name='MissingFace',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('bounding_box', models.TextField(default=None, null=True)),
                ('photo', models.ImageField(default=None, null=True, storage=facematch.storage_backends.MissingStorage(), upload_to='')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.MissingPerson')),
            ],
        ),
        migrations.CreateModel(
            name='FaceMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bounding_box', models.TextField(default=None, null=True)),
                ('similarity', models.IntegerField(default=None, null=True)),
                ('missing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.MissingFace')),
                ('missing_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.MissingPerson')),
                ('unidentified', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.UnidentifiedFace')),
            ],
            options={
                'verbose_name_plural': 'Face Matches',
            },
        ),
    ]
