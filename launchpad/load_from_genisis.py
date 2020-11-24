import sys
import os
import datetime as dt
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()


from rocketship.models import RegistrantData, iCData, studyTeamData, \
                            Record, HealthHistory, Gender, RaceEthnicity, \
                            Transportation, EmploymentStatus, Veteran


def create_unique_id(form_questions, created_datetime):
    # Django shell requiring these to be imported within the function (!)
    import hashlib
    import json
    import dateutil.parser
    hash_maker = hashlib.md5()
    hash_material = json.dumps(form_questions).encode()
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
    #fname = 'genisis_data.json'
    with open(fname) as infile:
        genisis_data = json.loads(infile.read())
    count = 0
    for submission in genisis_data:
        count += 1
        print(f'{count} of {len(genisis_data)}')
        submission_id = create_unique_id(
            submission['FormQuestions'],
            submission['CreatedDateTime']
        )
        try:
            queryset = Record.objects.get(submissionId=submission_id)
            if queryset:
                #print('Record found, skipping...')
                continue
        except Record.DoesNotExist:
            print('Creating new record...')

        registrant_data = create_registrant_data(submission['FormQuestions'])
        print(registrant_data)
        kwargs = {'formData': submission}
        for k, v in registrant_data.items():
            if k == 'HEALTH_HISTORY':
                kwargs[k] = HealthHistory(**{i: True for i in v})
                kwargs[k].save()
            elif k == 'EMPLOYMENT_STATUS':
                kwargs[k] = EmploymentStatus(**{i: True for i in v})
                kwargs[k].save()
            elif k == 'TRANSPORTATION':
                kwargs[k] = Transportation(**{i: True for i in v})
                kwargs[k].save()
            elif k == 'GENDER':
                kwargs[k] = Gender(**{i: True for i in v})
                kwargs[k].save()
            elif k == 'RACE_ETHNICITY':
                kwargs[k] = RaceEthnicity(**{i: True for i in v})
                kwargs[k].save()
            elif k == 'VETERAN':
                kwargs[k] = Veteran(**{i: True for i in v})
                kwargs[k].save()
            elif k == 'zipCode':
                kwargs[k] = v[0:5]
            elif k == 'veteranDateOfBirth':
                kwargs[k] = dt.datetime.strptime(v, '%Y-%m-%d')
            else:
                kwargs[k] = v

        registrant_data_obj = RegistrantData(**kwargs)

        ic_data_obj = iCData()
        study_team_data_obj = studyTeamData()
        record_obj = Record(
            submissionId=submission_id,
            registrantData=registrant_data_obj,
            iCData=ic_data_obj,
            studyTeamData=study_team_data_obj
        )
        for obj in [registrant_data_obj, ic_data_obj, study_team_data_obj,
                    record_obj]:
            obj.save()

if __name__ == '__main__':
    genisis_fname = sys.argv[1] # Should be the fn to read in
    main(fname=genisis_fname)

