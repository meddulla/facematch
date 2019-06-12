# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from people.models import MissingPerson
from people.utils import sync_missing_case_info

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py download_missing_case_info"


    def handle(self, *args, **options):
        missing_persons = MissingPerson.objects.filter(case_info_fetched=False)
        missing_persons = MissingPerson.objects.filter(height_from=None) # TODO tmp
        logger.info("Processsing %s missing person cases" % len(missing_persons))
        for person in missing_persons:
            logger.info("Processsing missing person %s" % person.code)
            sync_missing_case_info(person, force_sync=True)

