# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from django.conf import settings
from people.models import MissingFace
from people.utils import search_face
from aws.rekognition import Collection

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py search_all_for_matches"


    def handle(self, *args, **options):
        missing_faces = MissingFace.objects.filter(searched=False, is_face=True)
        logger.info("Searching %s missing faces for matches " % len(missing_faces))
        col_id = settings.REKOG_FACEMATCH_COLLECTION
        rekog = Collection(collection_id=col_id)
        for mface in missing_faces:
            search_face(mface, rekog=rekog)


