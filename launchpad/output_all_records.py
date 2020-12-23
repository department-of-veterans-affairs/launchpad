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


def main(outfile):
    relevant_records = Record.objects.all()
    relevant_record_list = []
    for rec in relevant_records:
        new_rec = create_row(rec)
        relevant_record_list.append(new_rec)
    relevant_df = pd.DataFrame.from_records(relevant_record_list)
    relevant_df.to_csv(outfile, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output all records.')
    parser.add_argument('--outfile_prefix', help='Outfile prefix',
        default="/home/ubuntu/launchpad/launchpad/data/all_records")
    args = parser.parse_args()
    today = dt.datetime.now()
    current_date = today.strftime("%Y_%m_%d_%H_%M")
    outfile = args.outfile_prefix + "/all_records_" + current_date + ".csv"
    main(outfile)
