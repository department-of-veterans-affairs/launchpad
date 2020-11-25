import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from rocketship.models import RegistrantData

all_records = RegistrantData.objects.all()
num_records = len(all_records)
print(f"Total num records: {num_records}")
