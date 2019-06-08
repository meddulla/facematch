# -*- coding: utf-8 -*-
import os
import time
import urllib
import logging
from django.core.management.base import BaseCommand
from people.models import MissingFace
from people.utils import process_case_image


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "./manage.py download_missing_cases"

    def add_arguments(self, parser):
        parser.add_argument('--directory', dest="directory", help='directory') #output
        parser.add_argument('--csv', dest="csv", help='csv')

    def handle(self, *args, **options):
        directory = options["directory"] or "media/images/missing"
        csv = options["csv"] or "missing-target.csv"

        # tpl = "https://www.namus.gov/api/CaseSets/NamUs/MissingPersons/Cases/9999/Images/68684/original"

        i = 0
        with open(csv) as f:
            for url in f:
                if i == 500:
                    i = 0
                    logger.info("Sleeping for 10s")
                    time.sleep(10)
                url = url.strip()
                case_id = url.split("/")[8]
                image_id = url.split("/")[10]
                image_name = "missing_%s_%s.jpg" % (case_id, image_id)


                case_dir = "%s/%s" % (directory, case_id)
                local_path = "%s/%s" % (case_dir, image_name)
                if os.path.exists(local_path):
                    logger.info("Skipped downloading from %s to %s" % (url, local_path))
                    continue
                elif MissingFace.objects.filter(photo=image_name).first():
                    logger.info("Skipped downloading from %s to %s. Image exists in missing face." % (url, local_path))
                    continue
                else:
                    if not os.path.exists(case_dir):
                        os.makedirs(case_dir)
                    logger.info("Downloading from %s to %s" % (url, local_path))
                    try:
                        urllib.request.urlretrieve(url, local_path)
                        process_case_image(case_id=case_id, img=image_name, local_path=local_path, is_missing=True)
                    except urllib.error.HTTPError as e:
                        logger.warning("Failed to download from %s to %s. Error: '%s'" % (url, local_path, str(e)))
                    i =+ 1
