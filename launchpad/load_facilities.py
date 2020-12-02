import json
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Facility

# Get this fron curl -X GET 'https://sandbox-api.va.gov/services/va_facilities/v0/facilities/all' --header 'apikey:...
fname = '/home/ubuntu/launchpad/launchpad/data/all_facilities.json'

with open(fname) as infile:
    facilities = json.loads(infile.read())['features']
completed = []
for facility in facilities:
    facility_id = facility['properties']['id'][0:7]
    if facility_id in completed:
        continue
    if 'vha' not in facility_id:
        continue
    facility_obj = Facility(
        facility_id=facility_id,
        name=facility['properties']['name'][0:100],
        zip_code=facility['properties']['address']['physical']['zip'][0:5],
        lat=facility['geometry']['coordinates'][1],
        lng=facility['geometry']['coordinates'][0],
    )
    completed.append(facility_id)
    facility_obj.save()
