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

OBJECTS = (
    ('-', '-'),
    ('belt_buckle', 'belt buckle'),
    ('tattoo', 'tattoo'),
    ('watch', 'watch'),
)

class Person(models.Model):
    code = models.CharField(max_length=400, default=None, null=True, unique=True)
    photo = models.ImageField(default=None, null=True)
    # Case info fields
    gender = models.CharField(
        max_length=2,
        choices=GENDERS,
        default='U',
    )
    ethnicity = models.CharField(max_length=400, default=None, null=True) # we only use the 1st one
    # control case info fields
    case_info_fetched = models.BooleanField(default=False)
    has_case_info = models.BooleanField(default=False)
    last_fetched = models.DateTimeField(default=None, null=True)


    def photo_tag(self):
        url = "https://%s/%s" % (MissingStorage.custom_domain, self.photo)
        return mark_safe('<img src="%s" width="200px"/>' % url)

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def __str__(self):
        return self.code

    class Meta:
        abstract = True
        ordering = ("code",)


class MissingPerson(Person):
    name = models.CharField(max_length=400, default=None, null=True)
    photo = models.ImageField(default=None, null=True, storage=MissingStorage())
    missing_min_age = models.IntegerField(default=None, null=True)
    missing_max_age = models.IntegerField(default=None, null=True)
    current_min_age = models.IntegerField(default=None, null=True)
    current_max_age = models.IntegerField(default=None, null=True)
    last_sighted = models.DateField(default=None, null=True)

    def __str__(self):
        return self.name or self.code

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        S3().delete_file(MissingStorage.bucket_name, file_name=self.photo)


class UnidentifiedPerson(Person):
    photo = models.ImageField(default=None, null=True, storage=UnidentifiedStorage())
    est_min_age = models.IntegerField(default=None, null=True)
    est_max_age = models.IntegerField(default=None, null=True)
    est_year_of_death_from = models.IntegerField(default=None, null=True)
    date_found = models.DateField(default=None, null=True)

    def photo_tag(self):
        url = "https://%s/%s" % (UnidentifiedStorage.custom_domain, self.photo)
        return mark_safe('<img src="%s" width="200px"/>' % url)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        S3().delete_file(UnidentifiedStorage.bucket_name, file_name=self.photo)



class Face(models.Model):
    id = models.UUIDField(primary_key=True) # rekog FaceId
    bounding_box = models.TextField(default=None, null=True)
    is_face = models.BooleanField(default=True)
    in_collection = models.BooleanField(default=True) # in rekog collection

    class Meta:
        abstract = True
        ordering = ("person", "id")


class MissingFace(Face):
    id = models.UUIDField(primary_key=True) # rekog FaceId
    person = models.ForeignKey(MissingPerson, on_delete=models.CASCADE)
    photo = models.ImageField(default=None, null=True, storage=MissingStorage())
    searched = models.BooleanField(default=False)
    last_searched = models.DateTimeField(default=None, null=True)

    def photo_tag(self):
        url = "https://%s/%s" % (MissingStorage.custom_domain, self.photo)
        return mark_safe('<img src="%s" width="200px" alt="%s"/>' % (url, self.photo))

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        S3().delete_file(MissingStorage.bucket_name, file_name=str(self.photo))

    def __str__(self):
        return "%s (missing case %s)" % (self.id, self.person.code)

    class Meta:
        ordering = ("person", "id")


class UnidentifiedFace(Face):
    person = models.ForeignKey(UnidentifiedPerson, on_delete=models.CASCADE)
    photo = models.ImageField(default=None, null=True, storage=UnidentifiedStorage())
    object_type = models.CharField(
        max_length=100,
        choices=OBJECTS,
        default='-',
        null=True,
    )

    def photo_tag(self):
        url = "https://%s/%s" % (UnidentifiedStorage.custom_domain, self.photo)
        return mark_safe('<img src="%s" width="200px" alt="%s"/>' % (url, self.photo))

    photo_tag.short_description = 'Image'
    photo_tag.allow_tags = True

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        S3().delete_file(UnidentifiedStorage.bucket_name, file_name=str(self.photo))

    def __str__(self):
        return "%s (unidentified case %s)" % (self.id, self.person.code)

    class Meta:
        ordering = ("person", "id")


class FaceMatch(models.Model):
    missing = models.ForeignKey(MissingFace, on_delete=models.CASCADE)
    missing_person = models.ForeignKey(MissingPerson, on_delete=models.CASCADE)
    bounding_box = models.TextField(default=None, null=True)
    similarity = models.IntegerField(default=None, null=True)
    unidentified = models.ForeignKey(UnidentifiedFace, on_delete=models.CASCADE)
    human_says_maybe = models.BooleanField(default=False)
    human_verified = models.BooleanField(default=False)
    case_info_checked = models.BooleanField(default=False)
    case_info_last_checked = models.DateTimeField(default=None, null=True)
    case_info_matches = models.BooleanField(default=False)
    case_info_reasons_non_match = models.TextField(default=None, null=True)

    def missing_tag(self):
        return self.missing.photo_tag()

    missing_tag.short_description = 'Missing'
    missing_tag.allow_tags = True

    def unidentified_tag(self):
        return self.unidentified.photo_tag()

    unidentified_tag.short_description = 'Unidentified'
    unidentified_tag.allow_tags = True

    def mnameus_link(self):
        url = "https://www.namus.gov/MissingPersons/Case#/%s/details" % self.missing_person.code
        return mark_safe('<a href="%s" target="_blank">Missing NamUs Case</a>' % url)

    mnameus_link.short_description = 'Missing NamUs'
    mnameus_link.allow_tags = True

    def unameus_link(self):
        url = "https://www.namus.gov/UnidentifiedPersons/Case#/%s/details" % self.unidentified.person.code
        return mark_safe('<a href="%s" target="_blank">Unidentified NamUs Case</a>' % url)

    unameus_link.short_description = 'Unidentified NamUs'
    unameus_link.allow_tags = True

    class Meta:
        verbose_name_plural = 'Face Matches'
        ordering = ("-id",)

class RandomImage(models.Model):
    description = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='images/random/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

