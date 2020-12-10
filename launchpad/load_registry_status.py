""" Load registry status of all records that have alread been sent out """

import os
import datetime as dt
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Record, RegistrantData

infilename = "/home/ubuntu/all_records_in_use.csv"

infile = open(infilename, 'r')

missing = []

i = 0
for line in infile:
    i += 1
    if i % 100 == 0:
        print(i)
    registrant = line.strip().split(",")
    if registrant[0] == 'firstName':
        continue # header row
    first_name = registrant[0]
    email = registrant[1]
    phone = registrant[2]
    relevant_records = Record.objects.filter(registrantData__firstName=email)
    if len(relevant_records) == 0:
        relevant_records = Record.objects.filter(registrantData__firstName=phone)
    if len(relevant_records) == 0:
        missing.append([registrant])
        continue
    if len(relevant_records) > 1:
        num = len(relevant_records)
        print(f"Multiple for {email} {num}")
    for rec in relevant_records:
        if registrant[3] == 'studyTeam':
            updateStatus = 'ST'
        elif registrant[3] == ['icScreen', 'ICScreen']:
            updateStatus = 'IC'
        else:
            print(f"Problem with updatestatus {registrant[3]}")
        rec.registryStatus = updateStatus
        today = dt.datetime.now()
        current_date = today.strftime('%Y-%m-%dT%H:%M:%SZ')
        rec.recordLastModifiedDateTime = dt.datetime.strptime(current_date, '%Y-%m-%dT%H:%M:%SZ')
        rec.save(update_fields=['registryStatus', 'recordLastModifiedDateTime'])

infile.close()
num_missing = len(missing)
print(f"Num missing {num_missing}")
print(missing)
