from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = True


class MissingStorage(S3Boto3Storage):
    location = ''
    file_overwrite = True
    bucket_name = "face-match-missing" # 'http://face-match-missing.s3.amazonaws.com/'
    custom_domain = '%s.s3.amazonaws.com' % bucket_name


class UnidentifiedStorage(S3Boto3Storage):
    location = ''
    file_overwrite = True
    bucket_name = "face-match-unidentified" #'http://face-match-unidentified.s3.amazonaws.com/'
    custom_domain = '%s.s3.amazonaws.com' % bucket_name
