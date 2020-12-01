""" Output new list of registrants for each site """


import os

from datetime import date
import argparse
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import RegistrantData
from rocketship.config import study_sites


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


def is_relevant_record(record, facility, max_dist):
    """ All requirements to apply here """
    distance_to_va = record.distance_to_vha(vha_code=facility)
    if distance_to_va is None:
        print("Problem getting distance to va")
        return False
    if distance_to_va <= max_dist and record.registryStatus == 'IN':
        return True
    else:
        return False


def main(facility, outfile, updateStatus=None):

    records_to_output = []

    all_records = RegistrantData.objects.all()

    for record in all_records:
        if is_relevant_record(record, facility, MAX_DIST_TO_VA):
            records_to_output.append(record)
            if updateStatus != None:
                record.registryStatus = updateStatus
                record.save(update_fields=['registryStatus'])

    num_records = len(records_to_output)
    print(f'Total number records to output {num_records}')

    output = serialize_records(records_to_output)

    file = open(outfile, 'w', newline='')
    file.write('submissionId,registryStatus,createdDateTime,firstName,middle,lastName,suffix,phone,email,zipCode,veteranDateOfBirth,GENDER,GENDER_SELF_IDENTIFY_DETAILS,RACE_ETHNICITY,VETERAN,diagnosed,closeContactPositive,hospitalized,smokeOrVape,HEALTH_HISTORY,EMPLOYMENT_STATUS,TRANSPORTATION,residentsInHome,closeContact,consentAgreementAccepted,timezone,state,age,iCRepresentativeName,iCLatestCallDate,iCoptOut,iCCallBackNeeded,iCCallBackDate,iCCallBackTime,iCReceivedOtherC19Vaccine,iCComments,iCLastModifiedDate,iCInUseBy,iCReadyforStudyTeam,studyTeamOptOut,studyTeamEligibilityOutcome,studyTeamEnrollmentStatus,studyTeamComments,studyTeamName\n')
    for line in output:
        file.write(line + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output study lists.')
    parser.add_argument('--outfile_prefix', help='Outfile prefix',
        required=True)
    parser.add_argument('--updateStatus', choices=['IC', 'ST'],
        help='What to update the status to. Not passing argument means no updating')
    args = parser.parse_args()

    today = date.today()
    current_date = today.strftime("%Y_%m_%d_%H_%M")
    for facility in study_sites:
        outfile = args.outfile_prefix + "/" + current_date + "_" + facility
        main(facility, outfile, args.updateStatus)
