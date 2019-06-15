# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from people.utils import verify_match
from people.models import FaceMatch

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py verify_matches"


    def handle(self, *args, **options):
        matches = FaceMatch.objects.filter(human_verified=False, human_says_maybe=False)
        logger.info("Verifying %s matches" % len(matches))
        for match in matches:
            verify_match(match)

