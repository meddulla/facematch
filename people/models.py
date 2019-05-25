from aws.s3 import S3
from django.db import models
from django.utils.safestring import mark_safe
from facematch.storage_backends import MissingStorage, UnidentifiedStorage

# Create your models here.
GENDERS = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('U', 'Unknown'),
)

CATEGORIES = (
    ('M', 'Missing'),
    ('U', 'Unidentified'),
)


class MissingPerson(models.Model):
    name = models.CharField(max_length=400, default=None, null=True)
    code = models.CharField(max_length=400, default=None, null=True, unique=True)
    gender = models.CharField(
        max_length=2,
        choices=GENDERS,
        default='U',
    )
    photo = models.ImageField(default=None, null=True, storage=MissingStorage())

    def photo_tag(self):
        url = "https://%s/%s" % (MissingStorage.custom_domain, self.photo)
        print(self.photo)
        print(url)
        return mark_safe('<img src="%s" />' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        S3().delete_file(MissingStorage.bucket_name, file_name=self.photo)

    def __str__(self):
        return self.name or self.code


class UnidentifiedPerson(models.Model):
    code = models.CharField(max_length=400, default=None, null=True, unique=True)
    gender = models.CharField(
        max_length=2,
        choices=GENDERS,
        default='U',
    )
    photo = models.ImageField(default=None, null=True, storage=UnidentifiedStorage())

    def photo_tag(self):
        url = "https://%s/%s" % (UnidentifiedStorage.custom_domain, self.photo)
        return mark_safe('<img src="%s" />' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        S3().delete_file(UnidentifiedStorage.bucket_name, file_name=self.photo)

    def __str__(self):
        return self.code


class MissingFace(models.Model):
    id = models.UUIDField(primary_key=True) # rekog FaceId
    bounding_box = models.TextField(default=None, null=True)
    person = models.ForeignKey(MissingPerson, on_delete=models.CASCADE)
    photo = models.ImageField(default=None, null=True, storage=MissingStorage())

    def photo_tag(self):
        url = "https://%s/%s" % (MissingStorage.custom_domain, self.photo)
        return mark_safe('<img src="%s" />' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        S3().delete_file(MissingStorage.bucket_name, file_name=str(self.photo))


class UnidentifiedFace(models.Model):
    id = models.UUIDField(primary_key=True) # rekog FaceId
    bounding_box = models.TextField(default=None, null=True)
    person = models.ForeignKey(UnidentifiedPerson, on_delete=models.CASCADE)
    photo = models.ImageField(default=None, null=True, storage=UnidentifiedStorage())

    def photo_tag(self):
        url = "https://%s/%s" % (UnidentifiedStorage.custom_domain, self.photo)
        return mark_safe('<img src="%s" />' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        S3().delete_file(UnidentifiedStorage.bucket_name, file_name=str(self.photo))


class FaceMatch(models.Model):
    missing = models.ForeignKey(MissingFace, on_delete=models.CASCADE, related_name="face_id")
    unidentified = models.ForeignKey(UnidentifiedFace, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Face Matches'
