""" Output new list of registrants for each site """

import os
from collections import OrderedDict
import datetime as dt
from datetime import date
import argparse
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

pd.set_option('display.max_columns', 500)

from rocketship.models import Facility, Record
from rocketship.config import study_sites
from rocketship.utilities.serializers import RecordSerializer


listOrder = ['submissionId', 'registryStatus', 'createdDateTime', 'firstName', 'middle', 'lastName',
    'suffix', 'phone', 'email', 'zipCode', 'veteranDateOfBirth', 'GENDER', 'GENDER_SELF_IDENTIFY_DETAILS',
    'RACE_ETHNICITY', 'VETERAN', 'diagnosed', 'closeContactPositive', 'hospitalized', 'smokeOrVape',
    'HEALTH_HISTORY', 'EMPLOYMENT_STATUS', 'TRANSPORTATION', 'residentsInHome', 'closeContact',
    'consentAgreementAccepted', 'timezone', 'state', 'age']

complicated_things = ['GENDER', 'RACE_ETHNICITY', 'VETERAN', "HEALTH_HISTORY", "EMPLOYMENT_STATUS", "TRANSPORTATION"]

initialList = ['submissionId', 'registryStatus', 'createdDateTime']

regList = ['firstName', 'middle', 'lastName',
    'suffix', 'phone', 'email', 'zipCode', 'veteranDateOfBirth', 'GENDER', 'GENDER_SELF_IDENTIFY_DETAILS',
    'RACE_ETHNICITY', 'VETERAN', 'diagnosed', 'closeContactPositive', 'hospitalized', 'smokeOrVape',
    'HEALTH_HISTORY', 'EMPLOYMENT_STATUS', 'TRANSPORTATION', 'residentsInHome', 'closeContact',
    'consentAgreementAccepted', 'timezone', 'state', 'age']


def convert_to_string(my_dict):
    true_keys = [key for key,value in my_dict.items() if value == True]
    output_str = ', '.join([f'*{record}*' for record in true_keys])
    return output_str


def create_row(record):
    serialized_record = RecordSerializer(record)
    serialized_record_dict = dict(serialized_record.data)
    final_dict = OrderedDict()
    for item in initialList:
        final_dict[item] = serialized_record_dict[item]
    for item in regList:
        if item in complicated_things:
            str_value = convert_to_string(serialized_record_dict['registrantData'][item])
            final_dict[item] = str_value
        else:
            final_dict[item] = serialized_record_dict['registrantData'][item]
    return final_dict


def main(facility, outfile, updateStatus=None):

    # Get all records within 100 miles of facility
    facility_obj = Facility.objects.get(facility_id=facility)
    relevant_records = Record.objects.filter(registrantData__facilities_w_in_100_mi__in=[facility_obj],
        registryStatus='IN')

    if len(relevant_records) == 0:
        print(f"No relevant records for {facility}")
        return f"{facility} failed"

    relevant_record_list = []
    for rec in relevant_records:
        new_rec = create_row(rec)
        relevant_record_list.append(new_rec)
        if updateStatus is not None:
            rec.registryStatus = updateStatus
            today = date.today()
            current_date = today.strftime('%Y-%m-%dT%H:%M:%SZ')
            rec.recordLastModifiedDateTime = dt.datetime.strptime(current_date, '%Y-%m-%dT%H:%M:%SZ')
            rec.save(update_fields=['registryStatus', 'recordLastModifiedDateTime'])

    relevant_df = pd.DataFrame.from_records(relevant_record_list)
    relevant_df.to_csv(outfile, index=False, na_rep='')
    print(relevant_df.describe(include='all'))
    return f"{facility} success"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output study lists.')
    parser.add_argument('--outfile_prefix', help='Outfile prefix',
        required=True)
    parser.add_argument('--update_status', choices=['IC', 'ST'],
        help='What to update the status to. Not passing argument means no updating')
    args = parser.parse_args()

    today = date.today()
    current_date = today.strftime("%Y_%m_%d_%H_%M")
    successful_sites = []
    for facility in study_sites:
        outfile = args.outfile_prefix + "/" + facility + "_" + current_date + ".csv"
        successful = main(facility, outfile, args.update_status)
        successful_sites.append(successful)
    print(f"Completion Status: {successful_sites}")
