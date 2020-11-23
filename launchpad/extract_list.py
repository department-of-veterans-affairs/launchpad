import os
import sys
import csv

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import RegistrantData


def main(facility, outfile):
    
    records_to_output = []

    # Read file of facilities we can about - but just do one for now
    all_records = RegistrantData.objects.all()

    for record in all_records:
        distance_to_va = record.distance_to_vha(vha_code='vha_526')
        if distance_to_va is None:
            print("Problem Boo")
            continue
        if distance_to_va <= 100:
            print("YEP")
            records_to_output.append([record.firstName, record.lastName, record.zipCode])
    print(len(records_to_output))
    print(records_to_output[0:5])
    file = open(outfile, 'a+', newline='')
    with file:
        write = csv.writer(file)
        write.writerows(records_to_output)


if __name__ == '__main__':
    facility_list_fn = 'facility_list.txt'
    outfile_prefix = 'outfile_'
    facilities = []
    with open(facility_list_fn) as fn:
        for line in fn:
            facilities.append(line.strip())
    for facility in facilities:
        out_file = outfile_prefix + facility
        main(facility, out_file)
