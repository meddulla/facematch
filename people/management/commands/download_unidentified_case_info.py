# -*- coding: utf-8 -*-
from logging import getLogger
import requests
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from people.models import UnidentifiedPerson

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py download_unidentified_case_info"


    def handle(self, *args, **options):
        unidentified_persons = UnidentifiedPerson.objects.filter(case_info_fetched=False)
        unidentified_persons = UnidentifiedPerson.objects.filter(height_from=None) # TODO tmp
        logger.info("Processsing %s unidentified person cases" % len(unidentified_persons))
        for person in unidentified_persons:
            self.sync_unidentified_case_info(person)




