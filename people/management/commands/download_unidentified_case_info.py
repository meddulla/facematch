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
        for person in unidentified_persons:
            logger.info("Processsing unidentified person %s" % person.code)
            self.sync_unidentified_case_info(person)

    def sync_unidentified_case_info(self, person):
        # curl -H Content-type:application/json https://www.namus.gov/api/CaseSets/NamUs/MissingPersons/Cases/18174\?forReport\=false
        headers = {'Content-type': 'application/json'}
        url = 'https://www.namus.gov/api/CaseSets/NamUs/UnidentifiedPersons/Cases/{case_id}?forReport=false'.format(case_id=person.code)
        r = requests.get(url, headers=headers)

        person.case_info_fetched = True
        person.last_fetched = now()

        if r.status_code != requests.codes.ok:
            logger.info("Unable to fetch case info %s. Status code: %s" % (person.code, r.status_code))
            person.save()
            return

        info = r.json()
        subject_desc = info["subjectDescription"]
        person.est_min_age = subject_desc["estimatedAgeFrom"]
        person.est_max_age = subject_desc["estimatedAgeTo"]
        person.gender = subject_desc["sex"]["name"][0]
        person.ethnicity = ", ".join([eth["name"] for eth in subject_desc["ethnicities"]])
        person.has_case_info = True
        person.est_year_of_death_from = subject_desc["estimatedYearOfDeathFrom"]
        person.date_found = info["circumstances"]["dateFound"]
        person.save()
        logger.info("Processed unidentified person %s" % person.code)


