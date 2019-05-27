# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.conf import settings
from django.utils.timezone import now
from people.models import MissingFace, UnidentifiedFace, FaceMatch
from people.utils import search_face
from aws.rekognition import Collection

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py search_all_for_matches"


    def handle(self, *args, **options):
        missing_faces = MissingFace.objects.filter(searched=False, is_face=True)
        col_id = settings.REKOG_FACEMATCH_COLLECTION
        rekog = Collection(collection_id=col_id)
        for mface in missing_faces:
            search_face(mface, rekog=rekog)


