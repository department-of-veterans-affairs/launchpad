""" Load registry status of all records that have alread been sent out """

import os
import datetime as dt
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Record, RegistrantData

infilename = "/home/ubuntu/all_records_in_use.csv"

infile = open(infilename, 'r')

i = 0
for line in infile:
    i += 1
    if i % 100 == 0:
        print(i)
    registrant = line.strip().split(",")
    if registrant[0] == 'firstName':
        continue # header row
    relevant_records = Record.objects.filter(registrantData__firstName=registrant[0],
        registrantData__email=registrant[1],
        registrantData__phone=registrant[2])
    if len(relevant_records) > 1:
        print(relevant_records)
    for rec in relevant_records:
        if registrant[3] == 'studyTeam':
            updateStatus = 'ST'
        if registrant[3] == 'icScreen':
            updateStatus = 'IC'
        rec.registryStatus = updateStatus
        today = dt.datetime.now()
        current_date = today.strftime('%Y-%m-%dT%H:%M:%SZ')
        rec.recordLastModifiedDateTime = dt.datetime.strptime(current_date, '%Y-%m-%dT%H:%M:%SZ')
        rec.save(update_fields=['registryStatus', 'recordLastModifiedDateTime'])

infile.close()
