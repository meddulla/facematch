import os
import uuid
import urllib
import logging
import json
import requests


from django.conf import settings
from .models import MissingPerson, MissingFace, UnidentifiedPerson, UnidentifiedFace, FaceMatch
from django.db.utils import IntegrityError
from django.utils.timezone import now
from aws.s3 import S3
from aws.rekognition import Collection
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def process_case_image(case_id, img, local_path, is_missing):
    logger.info("Processing case image %s" % local_path)
    if is_missing:
        person, created = save_missing_case(case_id=case_id)
    else:
        person, created = save_unidentified_case(case_id=case_id)

    if created and is_missing:
        person = sync_missing_case_info(person)
    elif created:
        person = sync_unidentified_case_info(person)

    if not person.photo:
        person.photo = img
        person.save()

    # Upload to s3 and addFace to collection
    if is_missing:
        process_missing_face(local_path=local_path, person=person, img=img)
    else:
        process_unidentified_face(local_path=local_path, person=person, img=img)


def save_unidentified_case(case_id):
    person, created = UnidentifiedPerson.objects.get_or_create(code=case_id)
    if created or not person.est_min_age:
        person.code = case_id
        person.gender = "U"
        person.save()
        logger.info("Saved unidentified person %s. Created: %s" % (person.code, created))
    return person, created


def save_missing_case(case_id):
    person, created = MissingPerson.objects.get_or_create(code=case_id)
    if created or not person.name:
        person.code = case_id
        person.gender = "U"
        person.save()
        logger.info("Saved missing person %s. Created: %s" % (person.code, created))
    return person, created


def process_unidentified(directory):
    """
    Expect a dir layout:
    dir/
        person-code/
            image1.jog
            image2.jog
    """

    logger.info("Processing %s" % directory)

    for _, dirs, files in os.walk(directory):
        for dir in dirs:
            logger.info("Processing %s" % dir)
            person = save_unidentified_case(case_id=dir)

            for root, subdirs, images in os.walk("%s/%s" % (directory, dir)):
                logger.info("Processing images in %s" % dir)
                for img in images:
                    local_path = "%s/%s/%s" % (directory, dir, img)
                    if not person.photo:
                        person.photo = img
                        person.save()
                    process_unidentified_face(local_path=local_path, person=person, img=img)

    logger.info("Done!")


def process_missing(directory):
    """
    Expect a dir layout:
    directory/
        person-code/
            image1.jog
            image2.jog
    """
    logger.info("Processing %s" % directory)

    for _, dirs, files in os.walk(directory):
        for dir in dirs:
            logger.info("Processing %s" % dir)
            person = save_missing_case(case_id=dir)

            for root, subdirs, images in os.walk("%s/%s" % (directory, dir)):
                logger.info("Processing images in %s" % dir)
                for img in images:
                    local_path = "%s/%s/%s" % (directory, dir, img)
                    if not person.photo:
                        person.photo = img
                        person.save()

                    process_missing_face(local_path=local_path, person=person, img=img)

    logger.info("Done!")


def process_unidentified_face(local_path, person, img):
    bucket = settings.S3_UNIDENTIFIED_BUCKET
    col_id = settings.REKOG_FACEMATCH_COLLECTION
    col = Collection(collection_id=col_id)
    s3 = S3()
    uploaded = s3.upload_public_file(bucket_name=bucket, file_name=local_path)

    face = UnidentifiedFace.objects.filter(photo=img, person=person).first()

    if not face:
        try:
            ret = col.addFaceToCollection(bucket=bucket, photo_s3_path=img)
            if not ret:
                logger.error("Unable to add face %s of %s" % (img, person.code))
                face = UnidentifiedFace(person=person, id=uuid.uuid4(), is_face=False, photo=img)
                face.save()
                return
            face_id = ret["indexed"]["face_id"]
            face, created = UnidentifiedFace.objects.get_or_create(id=face_id, person=person)
            face.bounding_box = json.dumps(ret["indexed"]["bounding_box"])
            face.photo = img
            face.save()
            logger.info("Saved unidentified face %s" % face_id)
        except ClientError as e:
            logger.error("Unable to index unidentified face %s. Error: '%s'" % (img, str(e)))
    else:
        logger.info("Already processed image %s, face %s" % (img, face.id))


def process_missing_face(local_path, person, img):
    bucket = settings.S3_MISSING_BUCKET
    col_id = settings.REKOG_FACEMATCH_COLLECTION
    col = Collection(collection_id=col_id)
    s3 = S3()
    uploaded = s3.upload_public_file(bucket_name=bucket, file_name=local_path)
    face = MissingFace.objects.filter(photo=img, person=person).first()

    if not face:
        try:
            ret = col.addFaceToCollection(bucket=bucket, photo_s3_path=img)
            if not ret:
                logger.error("Unable to add face %s of %s" % (img, person.code))
                face = MissingFace(person=person, id=uuid.uuid4(), is_face=False, photo=img)
                face.save()
                return
            face_id = ret["indexed"]["face_id"]
            face, created = MissingFace.objects.get_or_create(person=person, id=face_id)
            face.bounding_box = json.dumps(ret["indexed"]["bounding_box"])
            face.photo = img
            face.is_person = True
            face.save()
            logger.info("Saved missing face %s" % face_id)
        except ClientError as e:
            logger.error("Unable to index missing face %s. Error: '%s'" % (img, str(e)))
    else:
        logger.info("Already processed image %s, face %s" % (img, face.id))


def verify_match(match):
    logger.info("Verifying match %s of missing case %s" % (match.id, match.missing_person.id))

    if match.human_says_maybe or match.human_verified:
        logger.info("Human says maybe or human_verified - skipping match %s of missing case %s" % (match.id, match.missing_person.id))
        return


    match.case_info_checked = True
    match.case_info_last_checked = now()
    match.case_info_reasons_non_match = ""

    if not match.unidentified.is_face:
        match.case_info_matches = False
        match.case_info_reasons_non_match = "Unidentified photo is not a face. "
        match.save()
        logger.info("Verified match %s of missing case %s. Reason: %s, matches: %s" % (match.id,
                                                                                       match.missing_person.id,
                                                                                       match.case_info_reasons_non_match,
                                                                                       match.case_info_matches))
        return

    if not match.missing.is_face:
        match.case_info_matches = False
        match.case_info_reasons_non_match = "Missing photo is not a face. "
        match.save()
        logger.info("Verified match %s of missing case %s. Reason: %s, matches: %s" % (match.id,
                                                                                       match.missing_person.id,
                                                                                       match.case_info_reasons_non_match,
                                                                                       match.case_info_matches))
        return

    missing_person = match.missing_person
    unidentified_person = match.unidentified.person

    if not missing_person.has_case_info:
        logger.info("No missing case info available")
        return
    if not unidentified_person.has_case_info:
        logger.info("No unidentified case info available")
        return

    # Case Checks
    matches, reasons_non_match = case_checks(missing_person, unidentified_person)

    if matches is not None:
        match.case_info_matches = matches
        assert not reasons_non_match, "reasons non match not empty"
    if reasons_non_match:
        match.case_info_reasons_non_match = "".join(reasons_non_match)
        assert not matches, "matches but there are reasons not to match"

    match.save()
    logger.info("Verified match %s of missing case %s. Reason: %s, matches: %s." % (match.id,
                                                                                    match.missing_person.id,
                                                                                    match.case_info_reasons_non_match,
                                                                                    match.case_info_matches))

def case_checks(missing_person, unidentified_person):
    matches = None
    reasons_non_match = []
    age_check, gender_check, ethnicity_check, death_vs_last_sighting, height_check = None, None, None, None, None

    if unidentified_person.est_max_age and missing_person.missing_min_age:
        if unidentified_person.est_max_age > missing_person.missing_min_age:
            age_check = True
        else:
            reasons_non_match.append("Age is not a match. ")
            age_check = False
    else:
        logger.info("No age")

    if unidentified_person.gender and missing_person.gender:
        if unidentified_person.gender == missing_person.gender:
            gender_check = True
        else:
            reasons_non_match.append("Gender is not a match. ")
            gender_check = False
    else:
        logger.info("No gender")

    # if unidentified_person.height_from and missing_person.height_from:
    # subject was adult when missing, so height may have decreased if many years passed
    # if computedMissingMinAge > 20 and last sighting
    # diff = missing_person.height_from - unidentified_person.height_from
    # if diff < 4: # TODO recheck
    #     height_check = True
    # else:
    #     match.case_info_reasons_non_match += "Height is not a match. "
    #     height_check = False
    # else:
    #     logger.info("No height")


    if unidentified_person.ethnicity and missing_person.ethnicity:
        if unidentified_person.ethnicity.lower().strip() in missing_person.ethnicity.lower().strip():
            ethnicity_check = True
        else:
            reasons_non_match.append("Ethnicity is not a match. ")
            ethnicity_check = False
    else:
        logger.info("No ethnicity")

    if missing_person.last_sighted and unidentified_person.date_found:
        if missing_person.last_sighted < unidentified_person.date_found:
            death_vs_last_sighting = True
        else:
            reasons_non_match.append("Last sighting after date of death. ")
            death_vs_last_sighting = False
    else:
        logger.info("No death_vs_last_sighting")

    checks = [age_check, gender_check, ethnicity_check, death_vs_last_sighting, height_check]
    clean_checks = [check for check in checks if check is not None]
    if clean_checks and all(clean_checks):
        matches = True
    elif False in checks:
        matches = False
    else:
        # all None's
        pass
    return matches, reasons_non_match


def search_face(mface, rekog):
    logger.info("Processsing missing face %s" % mface.id)
    matches = rekog.search_faces(str(mface.id))
    mface.searched = True
    mface.last_searched = now()
    mface.save()
    if not matches:
        logger.info("No match found for face %s" % mface.id)
    for match in matches:
        unid_face =  match["face_id"]
        logger.info("Creating match of face %s with unidentified %s" % (mface.id, unid_face))
        sim =  match["similarity"]
        bounding_box =  match["bounding_box"]

        try:
            fm, created = FaceMatch.objects.get_or_create(missing=mface,
                                                          unidentified_id=unid_face,
                                                          missing_person=mface.person)
            fm.similarity = sim
            fm.bounding_box = bounding_box
            fm.save()
            verify_match(fm)
        except IntegrityError as e:
            # Probably a face in the missing group, not unidentified
            logger.error("Unable to save match - probably a 'missing' face. Error: '%s'" % str(e))


def sync_missing_case_info(person, force_sync=False, info=False):
    # curl -H Content-type:application/json https://www.namus.gov/api/CaseSets/NamUs/MissingPersons/Cases/18174\?forReport\=false
    if person.has_case_info and not force_sync:
        logger.info("Skipping syncing missing case info")
        return person
    if not info:
        headers = {'Content-type': 'application/json'}
        url = 'https://www.namus.gov/api/CaseSets/NamUs/MissingPersons/Cases/{case_id}?forReport=false'.format(case_id=person.code)
        r = requests.get(url, headers=headers)

        person.case_info_fetched = True
        person.last_fetched = now()

        if r.status_code != requests.codes.ok:
            logger.info("Unable to fetch case info %s. Status code: %s" % (person.code, r.status_code))
            person.save()
            return person

        info = r.json()

    subject = info["subjectIdentification"]
    person.name = " ".join([subject.get("firstName", "").capitalize(),
                            subject.get("middleName", "").capitalize(),
                            subject.get("lastName", "").capitalize()]).strip()
    person.current_min_age = subject.get("currentMinAge")
    person.current_max_age = subject.get("currentMaxAge")
    person.missing_min_age = subject.get("computedMissingMinAge")
    person.missing_max_age = subject.get("computedMissingMaxAge")
    subject_desc = info["subjectDescription"]
    person.gender = subject_desc["sex"]["name"][0]

    if "heightFrom" in subject_desc:
        person.height_from = subject_desc["heightFrom"]

    if subject_desc.get("ethnicities"):
        person.ethnicity = ", ".join([eth["name"] for eth in subject_desc.get("ethnicities")])
    if info.get("sighting"):
        person.last_sighted = info["sighting"]["date"]
    person.has_case_info = True
    person.save()
    logger.info("Processed missing person %s" % person.code)
    return person


def sync_unidentified_case_info(person, force_sync=False, info=False):
    # curl -H Content-type:application/json https://www.namus.gov/api/CaseSets/NamUs/MissingPersons/Cases/18174\?forReport\=false
    if person.has_case_info and not force_sync:
        logger.info("Skipping syncing unidentified case info")
        return person
    logger.info("Processsing unidentified person %s" % person.code)
    if not info:
        headers = {'Content-type': 'application/json'}
        url = 'https://www.namus.gov/api/CaseSets/NamUs/UnidentifiedPersons/Cases/{case_id}?forReport=false'.format(case_id=person.code)
        r = requests.get(url, headers=headers)

        person.case_info_fetched = True
        person.last_fetched = now()

        if r.status_code != requests.codes.ok:
            logger.info("Unable to fetch case info %s. Status code: %s" % (person.code, r.status_code))
            person.save()
            return person

        info = r.json()
    subject_desc = info["subjectDescription"]
    person.est_min_age = subject_desc.get("estimatedAgeFrom")
    person.est_max_age = subject_desc.get("estimatedAgeTo")
    person.gender = subject_desc["sex"]["name"][0]

    if "heightFrom" in subject_desc:
        person.height_from = subject_desc["heightFrom"]
    if subject_desc.get("ethnicities"):
        person.ethnicity = ", ".join([eth["name"] for eth in subject_desc["ethnicities"]])
    person.has_case_info = True
    person.est_year_of_death_from = subject_desc.get("estimatedYearOfDeathFrom")
    if info.get("circumstances"):
        person.date_found = info["circumstances"]["dateFound"]
    person.save()
    logger.info("Processed unidentified person %s" % person.code)
    return person


def download_missing_url(url, directory):
    url = url.strip()
    case_id = url.split("/")[8]
    image_id = url.split("/")[10]
    image_name = "missing_%s_%s.jpg" % (case_id, image_id)
    case_dir = "%s/%s" % (directory, case_id)
    local_path = "%s/%s" % (case_dir, image_name)
    if os.path.exists(local_path):
        logger.info("Skipped downloading from %s to %s" % (url, local_path))
        return False
    elif MissingFace.objects.filter(photo=image_name).first():
        logger.info("Skipped downloading from %s to %s. Image exists in missing face." % (url, local_path))
        return False
    else:
        if not os.path.exists(case_dir):
            os.makedirs(case_dir)
        logger.info("Downloading from %s to %s" % (url, local_path))
        try:
            urllib.request.urlretrieve(url, local_path)
        except urllib.error.HTTPError as e:
            logger.warning("Failed to download from %s to %s. Error: '%s'" % (url, local_path, str(e)))

        process_case_image(case_id, image_name, local_path=local_path, is_missing=True)
        return True
