""" Output statistics on all registrants by site """
import os
import datetime as dt
import argparse
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

pd.set_option('display.max_columns', 500)
from rocketship.models import Facility, Record
from rocketship.config import study_sites
from extract_registrants_for_studies import create_row


def output_stats(df, outfile, facility):
    out_log = outfile + ".log"
    with open(out_log, "a") as outfile:
        outfile.write(facility + "\n")
    df["age_bin"] = pd.cut(df["age"], [-1, 17, 40, 65, 120])
    age_df = df["age_bin"].value_counts().reset_index()
    age_df["AGE_PERCENT"] = age_df["age_bin"] / age_df["age_bin"].sum()
    age_df.to_csv(out_log, index=False, mode="a")
    gender_df = df["GENDER"].value_counts().reset_index()
    gender_df["GENDER_PERCENT"] = gender_df["GENDER"] / gender_df["GENDER"].sum()
    gender_df.to_csv(out_log, index=False, mode="a")
    ethnicity_df = df["RACE_ETHNICITY"].value_counts().reset_index()
    ethnicity_df["RACE_ETHNICITY_PERCENT"] = ethnicity_df["RACE_ETHNICITY"] / ethnicity_df["RACE_ETHNICITY"].sum()
    ethnicity_df.to_csv(out_log, index=False, mode="a")
    veteran_df = df["VETERAN"].value_counts().reset_index()
    veteran_df["VETERAN_PERCENT"] = veteran_df["VETERAN"] / veteran_df["VETERAN"].sum()
    veteran_df.to_csv(out_log, index=False, mode="a")
    # Adding registry status
    facility_obj = Facility.objects.get(facility_id=facility)
    in_records = len(Record.objects.filter(
        registrantData__facilities_w_in_100_mi__in=[facility_obj]
        ).exclude(
        iCData__iCOptOut=True
        ).exclude(
        studyTeamData__studyTeamOptOut="True"
        ).filter(registryStatus='IN'))
    st_records = len(Record.objects.filter(
        registrantData__facilities_w_in_100_mi__in=[facility_obj]
        ).exclude(
        iCData__iCOptOut=True
        ).exclude(
        studyTeamData__studyTeamOptOut="True"
        ).filter(registryStatus='ST'))
    ic_records = len(Record.objects.filter(
        registrantData__facilities_w_in_100_mi__in=[facility_obj]
        ).exclude(
        iCData__iCOptOut=True
        ).exclude(
        studyTeamData__studyTeamOptOut="True"
        ).filter(registryStatus='IC'))
    with open(out_log, 'a') as outfile:
        outfile.write("Status\n")
        outfile.write(f"Indexed,not sent: {in_records}\n")
        outfile.write(f"Sent to study teams: {st_records}\n")
        outfile.write(f"Sent to call centers: {ic_records}\n")


def main(facility, outfile):
    # Get all records within 100 miles of facility
    facility_obj = Facility.objects.get(facility_id=facility)
    relevant_records = Record.objects.filter(
        registrantData__facilities_w_in_100_mi__in=[facility_obj]
        ).exclude(
        iCData__iCOptOut=True
        ).exclude(
        studyTeamData__studyTeamOptOut="True"
        )
    if len(relevant_records) == 0:
        print(f"No relevant records for {facility}")
        return f"{facility} failed"
    relevant_record_list = []
    for rec in relevant_records:
        new_rec = create_row(rec)
        relevant_record_list.append(new_rec)
    relevant_df = pd.DataFrame.from_records(relevant_record_list)
    output_stats(relevant_df, outfile, facility)
    return f"{facility} success"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output study lists.')
    parser.add_argument('--outfile_prefix', help='Outfile prefix',
        default="/home/ubuntu/launchpad/launchpad/data/general_stats")
    args = parser.parse_args()
    today = dt.datetime.now()
    current_date = today.strftime("%Y_%m_%d_%H_%M")
    successful_sites = []
    for facility in study_sites:
        if not os.path.exists(args.outfile_prefix):
            os.makedirs(args.outfile_prefix)
        outfile = args.outfile_prefix + "/" + current_date + ".csv"
        successful = main(facility, outfile)
        successful_sites.append(successful)
    print(f"Completion Status: {successful_sites}")