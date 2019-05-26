#!/bin/bash


rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py clear_collection
python manage.py process_missing
python manage.py process_unidentified
python manage.py search_all_for_matches
