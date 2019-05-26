import os
import uuid
import logging
import json

from django.conf import settings
from .models import MissingPerson, MissingFace, UnidentifiedPerson, UnidentifiedFace
from aws.s3 import S3
from aws.rekognition import Collection


logger = logging.getLogger(__name__)


def process_unidentified(directory):
    """
    Expect a dir layout:
    dir/
        person-code/
            image1.jog
            image2.jog
    """
    bucket = settings.S3_UNIDENTIFIED_BUCKET
    col_id = settings.REKOG_FACEMATCH_COLLECTION
    col = Collection(collection_id=col_id)
    s3 = S3()

    logger.info("Processing %s" % directory)

    for _, dirs, files in os.walk(directory):
        for dir in dirs:
            logger.info("Processing %s" % dir)
            person, created = UnidentifiedPerson.objects.get_or_create(code=dir)
            person.code = dir
            person.gender = "U"
            person.save()
            logger.info("Saved unidentified person %s. Created: %s" % (person.code, created))

            for root, subdirs, images in os.walk("%s/%s" % (directory, dir)):
                logger.info("Processing images in %s" % dir)
                for img in images:
                    local_path = "%s/%s/%s" % (directory, dir, img)
                    if not person.photo:
                        person.photo = img
                        person.save()

                    uploaded = s3.upload_public_file(bucket_name=bucket, file_name=local_path)

                    face = UnidentifiedFace.objects.filter(photo=img, person=person).first()

                    if not face:
                        ret = col.addFaceToCollection(bucket=bucket, photo_s3_path=img)
                        if not ret:
                            logger.error("Unable to add face %s of %s" % (img, person.code))
                            face = UnidentifiedFace(person=person, id=uuid.uuid4(), is_face=False, photo=img)
                            face.save()
                            continue
                        face_id = ret["indexed"]["face_id"]
                        face, created = UnidentifiedFace.objects.get_or_create(id=face_id, person=person)
                        face.bounding_box = json.dumps(ret["indexed"]["bounding_box"])
                        face.photo = img
                        face.save()
                        logger.info("Saved unidentified face %s" % face_id)
                    else:
                        logger.info("Already processed image %s, face %s" % (img, face.id))

    logger.info("Done!")



def process_missing(directory):
    """
    Expect a dir layout:
    directory/
        person-code/
            image1.jog
            image2.jog
    """
    bucket = settings.S3_MISSING_BUCKET
    col_id = settings.REKOG_FACEMATCH_COLLECTION
    col = Collection(collection_id=col_id)
    s3 = S3()

    logger.info("Processing %s" % directory)

    for _, dirs, files in os.walk(directory):
        for dir in dirs:
            logger.info("Processing %s" % dir)
            person, created = MissingPerson.objects.get_or_create(code=dir)
            person.code = dir
            person.gender = "U"
            person.save()
            logger.info("Saved missing person %s. Created: %s" % (person.code, created))

            for root, subdirs, images in os.walk("%s/%s" % (directory, dir)):
                logger.info("Processing images in %s" % dir)
                for img in images:
                    local_path = "%s/%s/%s" % (directory, dir, img)
                    if not person.photo:
                        person.photo = img
                        person.save()

                    uploaded = s3.upload_public_file(bucket_name=bucket, file_name=local_path)
                    face = MissingFace.objects.filter(photo=img, person=person).first()

                    if not face:
                        ret = col.addFaceToCollection(bucket=bucket, photo_s3_path=img)
                        if not ret:
                            logger.error("Unable to add face %s of %s" % (img, person.code))
                            face = MissingFace(person=person, id=uuid.uuid4(), is_face=False, photo=img)
                            face.save()
                            continue
                        face_id = ret["indexed"]["face_id"]
                        face, created = MissingFace.objects.get_or_create(person=person, id=face_id)
                        face.bounding_box = json.dumps(ret["indexed"]["bounding_box"])
                        face.photo = img
                        face.is_person = True
                        face.save()
                        logger.info("Saved missing face %s" % face_id)
                    else:
                        logger.info("Already processed image %s, face %s" % (img, face.id))

    logger.info("Done!")



