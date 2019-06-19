# -*- coding: utf-8 -*-
import os

from django.test import TestCase
from people.tests.fixtures import load_json_file_content, FIXTURE_DIR_PATH
from people.utils import sync_missing_case_info, sync_unidentified_case_info
from people.models import MissingPerson, UnidentifiedPerson


class TestCaseChecks(TestCase):

    def setUp(self):
        missing_file = os.path.join(FIXTURE_DIR_PATH, "missing-1.json")
        unidentified_file = os.path.join(FIXTURE_DIR_PATH, "unidentified-1.json")

        missing_info = load_json_file_content(missing_file)
        missing_person = MissingPerson(code=missing_info["id"])
        missing_person.save()
        self.missing_person = sync_missing_case_info(person=missing_person, info=missing_info)

        unidentified_info = load_json_file_content(unidentified_file)
        unidentified_person = UnidentifiedPerson(code=unidentified_info["id"])
        unidentified_person.save()
        self.unidentified_person = sync_unidentified_case_info(person=unidentified_person, info=unidentified_info)

    def test_age_check(self):
        # TODO
        pass



