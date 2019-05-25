# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from people.utils import process_missing


class Command(BaseCommand):
    help = "./manage.py process_missing"

    def add_arguments(self, parser):
        """..."""
        parser.add_argument('--directory', dest="directory", help='directory')

    def handle(self, *args, **options):
        directory = options["directory"] or "media/images/missing"
        process_missing(directory)
