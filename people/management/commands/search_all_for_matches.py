# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.conf import settings
from people.models import MissingFace, UnidentifiedFace, FaceMatch
from aws.rekognition import Collection

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py search_all_for_matches"


    def handle(self, *args, **options):
        missing_faces = MissingFace.objects.all()
        bucket = settings.S3_UNIDENTIFIED_BUCKET
        col_id = settings.REKOG_FACEMATCH_COLLECTION
        rekog = Collection(collection_id=col_id)
        for mface in missing_faces:
            logger.info("Processsing missing face %s" % mface.id)
            matches = rekog.search_faces(str(mface.id))
            print(matches)
            for match in matches:
                unid_face =  match["face_id"]
                logger.info("Creating match of face %s with unidentified %s" % (mface.id, unid_face))
                sim =  match["similarity"]
                bounding_box =  match["bounding_box"]

                try:
                    fm, created = FaceMatch.objects.get_or_create(missing=mface,
                                                                  unidentified_id=unid_face,
                                                                  missing_person=mface.person)
                    fm.similarity = sim
                    fm.bounding_box = bounding_box
                    fm.save()
                except IntegrityError as e:
                    # Probably a face in the missing group, not identified
                    logger.error("Unable to save match - probably a missing face. Error: '%s'" % str(e))

