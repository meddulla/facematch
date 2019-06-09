# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from django.conf import settings
from people.models import MissingFace, UnidentifiedFace
from aws.rekognition import Collection

logger = getLogger(__name__)


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class Command(BaseCommand):
    help = "./manage.py remove_non_faces_from_collection"


    def handle(self, *args, **options):
        col_id = settings.REKOG_FACEMATCH_COLLECTION
        rekog = Collection(collection_id=col_id)

        missing_faces = MissingFace.objects.filter(is_face=False, in_collection=True)
        faces = [str(face.id) for face in missing_faces]
        if faces:
            for group in chunker(faces, 4000):
                logger.info("Deleting missing %s faces" % len(group))
                rekog.delete_faces(group)
                missing_faces.filter(id__in=group).update(in_collection=False)
                logger.info("Updated %s missing faces" % len(group))

        unidentified_faces = UnidentifiedFace.objects.filter(is_face=False, in_collection=True)
        faces = [str(face.id) for face in unidentified_faces]
        if faces:
            for group in chunker(faces, 4000):
                logger.info("Deleting unidentified %s faces" % len(group))
                rekog.delete_faces(group)
                unidentified_faces.filter(id__in=group).update(in_collection=False)
                logger.info("Updated %s unidentified faces" % len(group))

        logger.info("Done!")
