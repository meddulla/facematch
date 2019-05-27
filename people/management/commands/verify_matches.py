# -*- coding: utf-8 -*-
from logging import getLogger
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.conf import settings
from django.utils.timezone import now
from people.models import MissingFace, UnidentifiedFace, FaceMatch
from aws.rekognition import Collection

logger = getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py verify_matches"


    def handle(self, *args, **options):
        matches = FaceMatch.objects.filter(case_info_checked=False)
        for match in matches:
            logger.info("Verifying match %s of missing case %s" % (match.id, match.missing_person.id))
            match.case_info_checked = True
            match.case_info_last_checked = now()
            match.case_info_reasons_non_match = ""

            if not match.unidentified.is_face:
                match.case_info_matches = False
                match.case_info_reasons_non_match = "Unidentified photo is not a face. "
                match.save()
                continue

            missing_person = match.missing_person
            unidentified_person = match.unidentified.person

            if not missing_person.has_case_info:
                logger.info("No missing case info available")
                continue
            if not unidentified_person.has_case_info:
                logger.info("No unidentified case info available")
                continue

            age_check, gender_check, ethnicity_check, death_vs_last_sighting = False, False, False, False


            if unidentified_person.est_min_age and missing_person.missing_max_age:
                if unidentified_person.est_max_age > missing_person.missing_min_age:
                    age_check = True
                else:
                    match.case_info_reasons_non_match += "Age is not a match. "

            if unidentified_person.gender and missing_person.gender:
                if unidentified_person.gender == missing_person.gender:
                    gender_check = True
                else:
                    match.case_info_reasons_non_match += "Gender is not a match. "

            if unidentified_person.ethnicity and missing_person.ethnicity:
                if unidentified_person.ethnicity.lower().strip() in missing_person.ethnicity.lower().strip():
                    ethnicity_check = True
                else:
                    match.case_info_reasons_non_match += "Ethnicity is not a match. "

            if missing_person.last_sighted and unidentified_person.date_found:
                print(missing_person.last_sighted)
                print(unidentified_person.date_found)
                if missing_person.last_sighted < unidentified_person.date_found:
                    death_vs_last_sighting = True
                else:
                    match.case_info_reasons_non_match += "Last sighting after date of death. "

            if None not in [age_check, gender_check, ethnicity_check, death_vs_last_sighting]:
                if age_check and gender_check and ethnicity_check and death_vs_last_sighting:
                    match.case_info_matches = True
                else:
                    match.case_info_matches = False

            match.save()
            logger.info("Verified match %s of missing case %s. Matches: %s" % (match.id, match.missing_person.id,
                                                                               match.case_info_matches))

