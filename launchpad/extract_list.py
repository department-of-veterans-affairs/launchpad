""" Output new list of registrants for each site """


import os
import sys
import csv

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import RegistrantData


MAX_DIST_TO_VA = 100 #In miles

def serialize_records(records):
    output = []
    for record in records:
        serialized = {
            'submissionId': record['submissionId'],
            'registryStatus': record['registryStatus'],
            'createdDateTime': record['createdDateTime']
        }
        for data_type in ['registrantData', 'calculatedData', 'iCData',
                          'studyTeamData']:
            for key in record[data_type]:
                if type(record[data_type][key]) == list:
                    value = ', '.join(
                                    [f'*{record}*' for record in
                                        record[data_type][key]])
                    serialized[key] = value
                elif key == 'zipCode':
                    if record[data_type][key][-1] != '-':
                        value = f'{record[data_type][key]}-'
                    else:
                        value = f'{record[data_type][key]}'
                    serialized[key] = value
                else:
                    serialized[key] = record[data_type][key]
        output.append(serialized)
    return output


def is_relevant_record(record, facility):
    distance_to_va = record.distance_to_vha(vha_code=facility)
    if distance_to_va is None:
        print("Problem getting distance to va")
        return False 


def main(facility, outfile):
    
    records_to_output = []

    # Read file of facilities we can about - but just do one for now
    all_records = RegistrantData.objects.all()

    for record in all_records:
        if is_relevant_record(record, facility):
            records_to_output.append(record)

    num_records = len(records_to_output)
    print(f'Total number records to output {num_records}')
    serialize_records(records_to_output)

    file = open(outfile, 'a+', newline='')
    with file:
        write = csv.writer(file)
        write.writerows(records_to_output)


if __name__ == '__main__':
    facility_list_fn = sys.argv[1]
    outfile_prefix = sys.argv[2]
    facilities = []
    with open(facility_list_fn) as fn:
        for line in fn:
            facilities.append(line.strip())
    for facility in facilities:
        out_file = outfile_prefix + facility
        main(facility, out_file)
