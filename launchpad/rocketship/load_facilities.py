from rocketship.models import Facility
import json

fname = 'all_facilities.json'

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
    facility_obj.save()
    completed.append(facility_id)
