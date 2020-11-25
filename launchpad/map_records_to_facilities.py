
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import Record, Facility
from rocketship.config import study_sites

ct = Record.objects.count()
for record in Record.objects.all():
    print(ct)
    ct -= 1
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
            pass
            # Log this.
