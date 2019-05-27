# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from django.conf import settings
from people.models import MissingFace, UnidentifiedFace
from aws.rekognition import Collection

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py remove_non_faces_from_collection"


    def handle(self, *args, **options):
        col_id = settings.REKOG_FACEMATCH_COLLECTION
        rekog = Collection(collection_id=col_id)

        missing_faces = MissingFace.objects.filter(is_face=False, in_collection=True)
        faces = [str(face.id) for face in missing_faces]
        if faces:
            logger.info("Deleting missing %s faces" % len(faces))
            rekog.delete_faces(faces)
            count, _ = missing_faces.delete()
            logger.info("Updated %s unidentified faces" % len(missing_faces))

        unidentified_faces = UnidentifiedFace.objects.filter(is_face=False, in_collection=True)
        faces = [str(face.id) for face in unidentified_faces]
        if faces:
            logger.info("Deleting unidentified %s faces" % len(faces))
            rekog.delete_faces(faces)
            unidentified_faces.update(in_collection=False)
            logger.info("Updated %s unidentified faces" % len(unidentified_faces))

        logger.info("Done!")
