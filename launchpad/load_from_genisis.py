import sys
import os
import datetime as dt
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()


import datetime as dt
import json
from rocketship.models import RegistrantData, iCData, studyTeamData, \
                            Record, HealthHistory, Gender, RaceEthnicity, \
                            Transportation, EmploymentStatus, Veteran
from django.db.utils import IntegrityError


def create_unique_id(form_questions, created_datetime):
    # Django shell requiring these to be imported within the function (!)
    import hashlib
    import json
    import dateutil.parser
    for i in form_questions:
        if i['QuestionName'] == 'firstName':
            firstName = i['QuestionValue']
        elif i['QuestionName'] == 'lastName':
            lastName = i['QuestionValue']
        elif i['QuestionName'] == 'email':
            email = i['QuestionValue']
        else:
            continue 
    hash_maker = hashlib.md5()
    hash_string = firstName + lastName + email
    hash_material = hash_string.encode()
    #hash_material = json.dumps(form_questions).encode()
    hash_maker.update(hash_material)
    hash_out = hash_maker.hexdigest()
    hash_as_int = int(hash_out, 16)
    short_hash = str(hash_as_int)[-10:]
    created_datetime = dateutil.parser.parse(created_datetime)
    year = str(created_datetime.year).zfill(2)
    month = str(created_datetime.month).zfill(2)
    day = str(created_datetime.day).zfill(2)
    hour = str(created_datetime.hour).zfill(2)
    minute = str(created_datetime.minute).zfill(2)
    second = str(created_datetime.second).zfill(2)
    return f'{year}{month}{day}{hour}{minute}{second}-{short_hash}'


def create_registrant_data(form_question_list):
    consolidated = {}
    for question in form_question_list:
        category = None
        type = question['QuestionName']
        value = question['QuestionValue']
        if '::' in type:
            category, type = type.split('::')
            type = type.lower()
            if value.lower() == 'yes':
                try:
                    consolidated[category].append(type)
                except KeyError:
                    consolidated[category] = [type]
        else:
            consolidated[type] = value
    return consolidated


def main(fname):
    with open(fname) as infile:
        genisis_data = json.loads(infile.read())
    pks = []
    for submission in genisis_data:
        submission_id = create_unique_id(
            submission['FormQuestions'],
            submission['CreatedDateTime']
        )
        if Record.objects.filter(submissionId=submission_id).exists():
            # Skip if submission id exists.
            continue
        registrant_data = create_registrant_data(submission['FormQuestions'])
        health_history = HealthHistory.objects.create(
            **{i: True for i in registrant_data['HEALTH_HISTORY']})
        health_history.save()

        employment_status = EmploymentStatus.objects.create(
            **{i: True for i in registrant_data['EMPLOYMENT_STATUS']})
        employment_status.save()

        transportation = Transportation.objects.create(
            **{i: True for i in registrant_data['TRANSPORTATION']})
        transportation.save()

        gender = Gender.objects.create(
            **{i: True for i in registrant_data['GENDER']})
        gender.save()

        race_ethnicity = RaceEthnicity.objects.create(
            **{i: True for i in registrant_data['RACE_ETHNICITY']})
        race_ethnicity.save()

        veteran = Veteran.objects.create(
            **{i: True for i in registrant_data['VETERAN']})
        veteran.save()

        registrant_data_obj = RegistrantData.objects.create(
            HEALTH_HISTORY=health_history,
            EMPLOYMENT_STATUS=employment_status,
            TRANSPORTATION=transportation,
            GENDER=gender,
            RACE_ETHNICITY=race_ethnicity,
            VETERAN=veteran,
            formData=submission,
            firstName=registrant_data['firstName'],
            middle=registrant_data.get('middle', ''),
            lastName=registrant_data['lastName'],
            suffix=registrant_data.get('suffix', ''),
            phone=registrant_data['phone'],
            email=registrant_data['email'],
            zipCode=registrant_data['zipCode'][0:5],
            veteranDateOfBirth=dt.datetime.strptime(
                registrant_data['veteranDateOfBirth'], '%Y-%m-%d'),
            GENDER_SELF_IDENTIFY_DETAILS=registrant_data.get(
                'GENDER_SELF_IDENTIFY_DETAILS', ''),
            diagnosed=registrant_data['diagnosed'],
            closeContactPositive=registrant_data['closeContactPositive'],
            hospitalized=registrant_data['hospitalized'],
            smokeOrVape=registrant_data['smokeOrVape'],
            residentsInHome=registrant_data['residentsInHome'],
            closeContact=registrant_data['closeContact'],
            consentAgreementAccepted=registrant_data[
                'consentAgreementAccepted'],
        )
        registrant_data_obj.save()

        ic_data_obj = iCData.objects.create()
        ic_data_obj.save()

        study_team_data_obj = studyTeamData.objects.create()
        study_team_data_obj.save()
        try:
            record_obj = Record(
                submissionId=submission_id,
                registrantData=registrant_data_obj,
                iCData=ic_data_obj,
                studyTeamData=study_team_data_obj,
                createdDateTime=dt.datetime.strptime(
                    submission['CreatedDateTime'], '%Y-%m-%dT%H:%M:%SZ')
                )
            record_obj.save()
        except IntegrityError:
            # Skip if submission already exists to prevent data being overwritten.
            pass
        pks.append(record_obj.pk)
    return pks


if __name__ == '__main__':
    genisis_fname = sys.argv[1] # Should be the fn to read in
    main(fname=genisis_fname)
