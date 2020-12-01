import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launchpad.settings')
django.setup()

from django.db.models import Count, Case, When, Value
from rocketship.models import RaceEthnicity, RegistrantData

fname = "/home/ubuntu/launchpad/launchpad/data/genisis_data.json"
with open(fname) as infile:
    genisis_data = json.loads(infile.read())


num_genisis_records = len(genisis_data)
print(f"Total num records in genisis json: {num_genisis_records}")

all_records = RegistrantData.objects.all()
num_records = len(all_records)
print(f"Total num records in postgres: {num_records}")

diversity_records = RaceEthnicity.objects.all()

diversity_stats = diversity_records.aggregate(
        amer_ind=Count(Case(When(american_indian_alaska_native=True, then=Value(1)))),
        asian=Count(Case(When(asian=True, then=Value(1)))),
        black_african_american=Count(Case(When(black_african_american=True, then=Value(1)))),
        hispanic=Count(Case(When(hispanic_latino_spanish_origin=True, then=Value(1)))),
        hawaiian=Count(Case(When(hawaiian_pacific_islander=True, then=Value(1)))),
        white=Count(Case(When(white=True, then=Value(1)))),
        other_race_ethnicity=Count(Case(When(other_race_ethnicity=True, then=Value(1)))),
        none_of_above=Count(Case(When(none_of_above=True, then=Value(1)))),
)

print("Updated diversity stats:")
print(f"Amer Ind: {diversity_stats['amer_ind']}")
print(f"Asian: {diversity_stats['asian']}")
print(f"Black/Afr: {diversity_stats['black_african_american']}")
print(f"Hispanic: {diversity_stats['hispanic']}")
print(f"Hawaiian: {diversity_stats['hawaiian']}")
print(f"White: {diversity_stats['white']}")
print(f"Other: {diversity_stats['other_race_ethnicity']}")
print(f"None: {diversity_stats['none_of_above']}")
