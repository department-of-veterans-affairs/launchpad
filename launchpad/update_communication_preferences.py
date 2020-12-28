""" Update communication preferences by adding it to the notes section
"""
import os
import datetime as dt
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Record, RegistrantData

FILENAME = "/home/ubuntu/launchpad/launchpad/data/update_lists/contact_prefs_20201228.csv"

def main():
    today = dt.datetime.now()
    current_date = today.strftime('%Y-%m-%dT%H:%M:%SZ')
    modify_time = dt.datetime.strptime(current_date, '%Y-%m-%dT%H:%M:%SZ')

    emails_phones_data = []
    with open(FILENAME, 'r') as infile:
        for line in infile:
            line_clean = line.strip().split(',')
            if line[0] == 'Last Name':
                continue
            emails_phones_data.append([line_clean[2], line_clean[3], line_clean[4]])

    for email_phone_data in emails_phones_data:
        email = email_phone_data[0].lower()
        phone = email_phone_data[1]
        data = email_phone_data[2]
        if len(Record.objects.filter(registrantData__email__iexact=email)) > 0:
            records = Record.objects.filter(registrantData__email__iexact=email)
        elif len(Record.objects.filter(registrantData__phone=phone)) > 0:
            records = Record.objects.filter(registrantData__phone=phone)
            print(f"Found phone: {phone}")
        else:
            continue
        for rec in records:
            if rec.registryStatus != 'IN':
                print(f"Record already sent off: {email}, {rec.registryStatus}")
            rec_registrantData = RegistrantData.objects.get(id=rec.registrantData_id)
            rec_registrantData.registrantDataLastModifiedDateTime = modify_time
            preferred_contact_info = "Preferred contact method: " + data
            print(preferred_contact_info)
            rec_registrantData.notes = preferred_contact_info
            rec_registrantData.save()

            print(f"Record updated: {email} {phone}")

if __name__ == '__main__':
    main()