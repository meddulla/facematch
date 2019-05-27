# -*- coding: utf-8 -*-
from logging import getLogger
import requests
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from people.models import MissingPerson

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py download_missing_case_info"


    def handle(self, *args, **options):
        missing_persons = MissingPerson.objects.filter(case_info_fetched=False)
        for person in missing_persons:
            logger.info("Processsing missing person %s" % person.code)
            self.sync_missing_case_info(person)

    def sync_missing_case_info(self, person):
        # curl -H Content-type:application/json https://www.namus.gov/api/CaseSets/NamUs/MissingPersons/Cases/18174\?forReport\=false
        headers = {'Content-type': 'application/json'}
        url = 'https://www.namus.gov/api/CaseSets/NamUs/MissingPersons/Cases/{case_id}?forReport=false'.format(case_id=person.code)
        r = requests.get(url, headers=headers)

        person.case_info_fetched = True
        person.last_fetched = now()

        if r.status_code != requests.codes.ok:
            print(r.text)
            logger.info("Unable to fetch case info %s. Status code: %s" % (person.code, r.status_code))
            person.save()
            return

        info = r.json()
        subject = info["subjectIdentification"]
        person.name = " ".join([subject.get("firstName", "").capitalize(),
                                subject.get("middleName", "").capitalize(),
                                subject.get("lastName", "").capitalize()]).strip()
        person.current_min_age = subject["currentMinAge"]
        person.current_max_age = subject["currentMaxAge"]
        person.missing_min_age = subject["computedMissingMinAge"]
        person.missing_max_age = subject["computedMissingMaxAge"]
        subject_desc = info["subjectDescription"]
        person.gender = subject_desc["sex"]["name"][0]
        person.ethnicity = ", ".join([eth["name"] for eth in subject_desc["ethnicities"]])
        person.last_sighted = info["sighting"]["date"]
        person.has_case_info = True
        person.save()
        logger.info("Processed missing person %s" % person.code)


