# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from people.utils import verify_match
from people.models import FaceMatch

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py verify_matches"


    def handle(self, *args, **options):
        matches = FaceMatch.objects.filter(case_info_checked=False)
        for match in matches:
            verify_match(match)
