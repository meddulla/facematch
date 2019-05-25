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
    code = models.CharField(max_length=400, default=None, null=True)
    gender = models.CharField(
        max_length=2,
        choices=GENDERS,
        default='U',
    )
    photo = models.ImageField(default=None, null=True, storage=MissingStorage())

    def photo_tag(self):
        url = "https://%s/%s/%s" % (MissingStorage.custom_domain, MissingStorage.location, self.photo)
        return mark_safe('<img src="%s" />' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def delete(self, *args, **kwargs):
        photo = "%s/%s" % (MissingStorage.location, self.photo)
        super().delete(*args, **kwargs)
        S3().delete_file(MissingStorage.bucket_name, file_name=photo)

    def __str__(self):
        return self.name


class UnidentifiedPerson(models.Model):
    code = models.CharField(max_length=400, default=None, null=True)
    gender = models.CharField(
        max_length=2,
        choices=GENDERS,
        default='U',
    )
    photo = models.ImageField(default=None, null=True, storage=UnidentifiedStorage())

    def photo_tag(self):
        url = "https://%s/%s/%s" % (UnidentifiedStorage.custom_domain, UnidentifiedStorage.location, self.photo)
        return mark_safe('<img src="%s" />' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def delete(self, *args, **kwargs):
        photo = "%s/%s" % (UnidentifiedStorage.location, self.photo)
        super().delete(*args, **kwargs)
        S3().delete_file(UnidentifiedStorage.bucket_name, file_name=photo)

    def __str__(self):
        return self.code


class MissingFace(models.Model):
    id = models.UUIDField(primary_key=True) # rekog FaceId
    person = models.ForeignKey(MissingPerson, on_delete=models.CASCADE)
    photo = models.ImageField(default=None, null=True, storage=MissingStorage())

    def photo_tag(self):
        url = "https://%s/%s/%s" % (MissingStorage.custom_domain, MissingStorage.location, self.photo)
        return mark_safe('<img src="%s" />' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True


class UnidentifiedFace(models.Model):
    id = models.UUIDField(primary_key=True) # rekog FaceId
    person = models.ForeignKey(UnidentifiedPerson, on_delete=models.CASCADE)
    photo = models.ImageField(default=None, null=True, storage=UnidentifiedStorage())

    def photo_tag(self):
        url = "https://%s/%s/%s" % (UnidentifiedStorage.custom_domain, UnidentifiedStorage.location, self.photo)
        return mark_safe('<img src="%s" />' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True


class FaceMatch(models.Model):
    missing = models.ForeignKey(MissingFace, on_delete=models.CASCADE, related_name="face_id")
    unidentified = models.ForeignKey(UnidentifiedFace, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Face Matches'
