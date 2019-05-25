import uuid
import boto3
import logging

logger = logging.getLogger(__name__)


class S3():
    # See https://realpython.com/python-boto3-aws-s3/#client-versus-resource
    s3 = boto3.resource('s3')

    def create_bucket_name(bucket_prefix):
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def create_temp_file(size, file_name, file_content, prefix=""):
        random_file_name = '_'.join(prefix, [str(uuid.uuid4().hex[:6]), file_name])
        with open(random_file_name, 'w') as f:
            f.write(str(file_content) * size)
        return random_file_name

    def create_bucket(self, bucket_name, is_prefix=False):
        session = boto3.session.Session()
        current_region = session.region_name
        if is_prefix:
            bucket_name = self.create_bucket_name(bucket_prefix=bucket_name)
        s3_client = self.s3.meta.client
        bucket_response = s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': current_region})
        logger.info("%s %s" % (bucket_name, current_region))
        return bucket_name, bucket_response

    def delete_bucket(self, bucket_name):
        return self.s3.Bucket(bucket_name).delete()

    def upload_file(self, bucket_name, file_name, extra={}):
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        key = file_name[file_name.rindex('/')+1:]
        print(key)
        self.s3.Object(bucket_name, key).upload_file(Filename=file_name, ExtraArgs=extra)
        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location, bucket_name, file_name)
        return object_url

    def upload_public_file(self, bucket_name, file_name):
        extra = {
            'ACL': 'public-read',
            'StorageClass': 'STANDARD_IA' # for infrequently used data that needs to be retrieved rapidly when requested
        }
        return self.upload_file(bucket_name=bucket_name, file_name=file_name, extra=extra)

    def download_file(self, bucket_name, file_name, dest_path="/tmp"):
        return self.s3.Object(bucket_name, file_name).download_file("%s/%s" % (dest_path, file_name))

    def delete_file(self, bucket_name, file_name):
        return self.s3.Object(bucket_name, file_name).delete()

    def get_files(self, bucket_name):
        bucket = self.s3.Bucket(bucket_name)
        return bucket.objects.all()
