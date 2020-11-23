import json
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Facility

fname = 'all_facilities.json'

with open(fname) as infile:
    facilities = json.loads(infile.read())['_default']


print('read file')
print("num facilities")
print(len(str(facilities.keys())))
completed = []
for facility_id, facility in facilities.items():
    facility_id = facility['data']['id'][0:7]
    if facility_id in completed:
        continue
    if 'vha' not in facility_id:
        continue
    try:
        yep = Facility.objects.get(facility_id=facility_id)
        continue
    except:
        facility_obj =Facility(
            facility_id=facility_id,
            name=facility['data']['attributes']['name'][0:100],
            zip_code=facility['data']['attributes']['address']['physical']['zip'][0:5],
            lat=facility['data']['attributes']['lat'],
            lng=facility['data']['attributes']['long'],
        )
        facility_obj.save()
        completed.append(facility_id)

print("COMPLETED")
print(len(completed))
