""" Opt registrants out of the registry who have emailed
    and said they are no longer interested in participating.
    First identify record by email and then, if that fails,
    by phone
"""
import os
import datetime as dt
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Record, iCData, studyTeamData

FILENAME = "/home/ubuntu/opt-outs-2020-12-3_formatted.csv"

def main():
    today = dt.datetime.now()
    current_date = today.strftime('%Y-%m-%dT%H:%M:%SZ')
    modify_time = dt.datetime.strptime(current_date, '%Y-%m-%dT%H:%M:%SZ')

    emails_phones = []
    with open(FILENAME, 'r') as infile:
        for line in infile:
            line_clean = line.strip().split(',')
            if line[0] == 'Last Name':
                continue
            emails_phones.append(line_clean[2], line_clean[3])

    for email_phone in emails_phones:
        email = email_phone[0].lower()
        phone = email_phone[1]
        if len(Record.objects.filter(registrantData__email=email)) > 0:
            records = Record.objects.filter(registrantData__email=email)
        elif len(Record.objects.filter(registrantData__phone=phone)) > 0:
            records = Record.objects.filter(registrantData__phone=phone)
            print(f"Found phone: {phone}")
        else:
            print(f"Failed to find: {email}")
            continue
        for rec in records:
            if rec.registryStatus != 'IN':
                print(f"Record already sent off: {email}, {rec.registryStatus}")
                rec_studyteam = studyTeamData.objects.get(id=rec.studyTeamData_id)
            rec_studyteam.studyTeamOptOut = "True"
            rec_studyteam.studyTeamLastModifiedDateTime = modify_time
            rec_studyteam.save()

            rec_icdata = iCData.objects.get(id=rec.icData_id)
            rec_icdata.iCOptOut = True
            rec_icdata.iCLastModifiedDateTime = modify_time
            rec_icdata.save()
            print(f"Record updated: {email}")


if __name__ == '__main__':
    main()
