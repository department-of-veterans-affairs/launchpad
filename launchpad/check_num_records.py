import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import RegistrantData

all_records = RegistrantData.objects.all()
print("Total num records")
print(len(all_records))
