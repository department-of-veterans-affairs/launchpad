""" Populates the facilities_w_in_100_mi portion of the record
    which can be used in the future for faster extraction of relevant
    participants
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Record, Facility
from rocketship.config import study_sites


def map_records_to_facilities_function(record):
    for site_code in study_sites:
        dist = record.registrantData.distance_to_vha(site_code)
        if not dist:
            continue
        if dist > 100:
            continue
        try:
            facility_obj = Facility.objects.get(
                            facility_id=site_code)
            record.registrantData.facilities_w_in_100_mi.add(
                            facility_obj)
            record.save()
        except Facility.DoesNotExist:
            print(f"Facility missing: {site_code}")


def main():
    for record in Record.objects.all():
        map_records_to_facilities_function(record)


if __name__ == '__main__':
    main()