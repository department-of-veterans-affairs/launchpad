""" Load registry status of all records that have alread been sent out """

import os
import sys
import datetime as dt
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Record, RegistrantData


def update_record(rec, newStatus, current_date):
    """ Update record with new status """
    if newStatus.lower() == 'studyteam':
        updateStatus = 'ST'
    elif newStatus.lower() == 'icscreen':
        updateStatus = 'IC'
    else:
        print(f"Problem with updatestatus {newStatus}")
    rec.registryStatus = updateStatus
    rec.recordLastModifiedDateTime = dt.datetime.strptime(current_date, '%Y-%m-%dT%H:%M:%SZ')
    rec.save(update_fields=['registryStatus', 'recordLastModifiedDateTime'])


def identify_records_with_email(registrant):
    """ Identify by email & if that doesn't work, try phone """
    email = registrant[1]
    phone = registrant[2]
    relevant_records = Record.objects.filter(registrantData__email=email)
    if len(relevant_records) == 0:
        relevant_records = Record.objects.filter(registrantData__phone=phone)
    return relevant_records


def identify_records_with_id(registrant):
    """ We only have the submissionId so just try that """
    relevant_records = Record.objects.filter(submissionId=registrant[0])
    return relevant_records


def num_with_each_status():
    in_records = len(Record.objects.filter(registryStatus='IN'))
    st_records = len(Record.objects.filter(registryStatus='ST'))
    ic_records = len(Record.objects.filter(registryStatus='IC'))
    print(f"IN: {in_records} ST: {st_records} IC: {ic_records}")


def main(infile, recordtype):
    # This will be the modified datetime in all the records
    today = dt.datetime.now()
    current_date = today.strftime('%Y-%m-%dT%H:%M:%SZ')

    total_num_in_file = len(open(infilename).readlines())
    print(f"Total lines in file {total_num_in_file}")

    num_with_each_status()
    infile = open(infile, 'r', encoding='utf-8-sig')

    missing = []
    multiple = []
    i = 0

    for line in infile:
        i += 1
        if i % 100 == 0:
            print(i)
        registrant = line.strip().split(",")
        if registrant[0] == 'firstName':
            print('header row!')
            continue # header row
        if recordtype in ['id_ic', 'id_st']:
            relevant_records = identify_records_with_id(registrant)
        elif recordtype == 'email':
            relevant_records = identify_records_with_email(registrant)
        else:
            print(f"Problem with updatestatus {recordtype}")
            sys.exit()
        if len(relevant_records) == 0:
            missing.append([registrant])
            continue
        if len(relevant_records) > 1:
            num = len(relevant_records)
            multiple.append(num)
        for rec in relevant_records:
            if recordtype == 'email':
                newStatus = registrant[3]
            elif recordtype == 'id_ic':
                newStatus = 'icScreen'
            elif recordtype == 'id_st':
                newStatus = 'studyTeam'
            else:
                print("Problem")
            update_record(rec, newStatus, current_date)
    infile.close()
    num_missing = len(missing)
    print(f"Num missing {num_missing}")
    print(missing)
    print("Duplicates")
    print(multiple)
    num_with_each_status()


if __name__ == '__main__':
    infilename = sys.argv[1]
    recordtype = sys.argv[2] # can be email, id_ic, id_st
    if recordtype not in ['email', 'id_ic', 'id_st']:
        print("Record type must be email or id")
        sys.exit()
    main(infilename, recordtype)

