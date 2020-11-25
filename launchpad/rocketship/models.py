import sys
from django.db import models
import datetime as dt
import zipcodes
from rocketship.config import TIME_ZONE_MAPPINGS
from rocketship.utilities.geography import distance_between_points


class Facility(models.Model):
    facility_id = models.CharField(max_length=7)
    lat = models.FloatField()
    lng = models.FloatField()
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=5)


class MultiSelectMixin(models.Model):

    class Meta:
        abstract = True

    def get_all_true_values(self):
        return [option.name for option in self._meta.get_fields()
                if (getattr(self, option.name, None) and option.name != 'id')]

    def get_all_options(self):
        return [option.name for option in self._meta.get_fields() if
                option.name != 'id']

    def get_all_options_and_values(self):
        return {option.name: getattr(self, option.name, None)
                for option in self._meta.get_fields() if option.name not in
                ['id', 'registrantdata']}


class Gender(MultiSelectMixin):
    male = models.BooleanField(null=True)
    female = models.BooleanField(null=True)
    transgender_male = models.BooleanField(null=True)
    transgender_female = models.BooleanField(null=True)
    non_binary = models.BooleanField(null=True)
    self_identify = models.BooleanField(null=True)
    none_of_above = models.BooleanField(null=True)


class RaceEthnicity(MultiSelectMixin):
    american_indian_alaska_native = models.BooleanField(null=True)
    asian = models.BooleanField(null=True)
    black_african_american = models.BooleanField(null=True)
    hispanic_latino_spanish_origin = models.BooleanField(null=True)
    hawaiian_pacific_islander = models.BooleanField(null=True)
    white = models.BooleanField(null=True)
    other_race_ethnicity = models.BooleanField(null=True)
    none_of_above = models.BooleanField(null=True)


class Veteran(MultiSelectMixin):
    veteran = models.BooleanField(null=True)
    active_duty = models.BooleanField(null=True)
    va_employee = models.BooleanField(null=True)
    family_member_caregiver = models.BooleanField(null=True)
    va_healthcare_champva = models.BooleanField(null=True)
    national_guard_reserves = models.BooleanField(null=True)
    none_of_above = models.BooleanField(null=True)


class HealthHistory(MultiSelectMixin):
    allergy_vaccine = models.BooleanField(null=True)
    autoimmune_disease = models.BooleanField(null=True)
    cancer = models.BooleanField(null=True)
    immunocompromised = models.BooleanField(null=True)
    diabetes = models.BooleanField(null=True)
    heart_disease = models.BooleanField(null=True)
    high_blood_pressure = models.BooleanField(null=True)
    kidney_liver_disease = models.BooleanField(null=True)
    lung_disease = models.BooleanField(null=True)
    stroke = models.BooleanField(null=True)
    another_serious_chronic_illness = models.BooleanField(null=True)
    none_of_above = models.BooleanField(null=True)


class EmploymentStatus(MultiSelectMixin):
    employed_home = models.BooleanField(null=True)
    employed_outside_of_home = models.BooleanField(null=True)
    frontline_worker = models.BooleanField(null=True)
    furloughed_unemployed = models.BooleanField(null=True)
    retired = models.BooleanField(null=True)
    student = models.BooleanField(null=True)
    none_of_above = models.BooleanField(null=True)


class Transportation(MultiSelectMixin):
    car = models.BooleanField(null=True)
    carpool_or_vanpool = models.BooleanField(null=True)
    frequent_air_travel = models.BooleanField(null=True)
    public_transport = models.BooleanField(null=True)
    walk_bike = models.BooleanField(null=True)
    work_from_home = models.BooleanField(null=True)
    none_of_above = models.BooleanField(null=True)


class RegistrantData(models.Model):
    firstName = models.CharField(max_length=200)
    middle = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    suffix = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    zipCode = models.CharField(max_length=5)
    veteranDateOfBirth = models.DateField()
    GENDER = models.ForeignKey('Gender', on_delete=models.PROTECT)
    GENDER_SELF_IDENTIFY_DETAILS = models.CharField(max_length=200)
    RACE_ETHNICITY = models.ForeignKey('RaceEthnicity',
                                       on_delete=models.PROTECT)
    VETERAN = models.ForeignKey('Veteran', on_delete=models.PROTECT)
    diagnosed = models.CharField(max_length=200)
    closeContactPositive = models.CharField(max_length=200)
    hospitalized = models.CharField(max_length=200)
    smokeOrVape = models.CharField(max_length=200)
    HEALTH_HISTORY = models.ForeignKey('HealthHistory',
                                       on_delete=models.PROTECT)
    EMPLOYMENT_STATUS = models.ForeignKey(
                        'EmploymentStatus', on_delete=models.PROTECT)
    TRANSPORTATION = models.ForeignKey(
                        'Transportation', on_delete=models.PROTECT)
    residentsInHome = models.CharField(max_length=200)
    closeContact = models.CharField(max_length=200)
    consentAgreementAccepted = models.CharField(max_length=200)
    # Original data.
    formData = models.JSONField()
    # Near facilities
    facilities_w_in_100_mi = models.ManyToManyField(Facility)
    # Timestamps.
    registrantDataLastModifiedDateTime = models.DateTimeField(auto_now=True)
    registrantDataCreatedDateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<RegistrantData {self.firstName} {self.lastName}>'

    @property
    def age(self):
        return int((dt.date.today() - self.veteranDateOfBirth).days/365.25)

    @property
    def state(self):
        match = zipcodes.matching(f'{self.zipCode[0:5]}')
        if match:
            return match[0]['state']
        return None

    @property
    def timezone(self):
        match = zipcodes.matching(f'{self.zipCode[0:5]}')
        if match:
            return match[0]['timezone']
        return None

    @property
    def lat_lng(self):
        match = zipcodes.matching(f'{self.zipCode[0:5]}')
        if match:
            return (float(match[0]['lat']), float(match[0]['long']))
        return None

    def distance_to_vha(self, vha_code):
        try:
            facility_info = Facility.objects.get(facility_id=vha_code)
        except Facility.DoesNotExist:
            return None
        record_lat_lng = self.lat_lng
        if not record_lat_lng:
            return None
        return distance_between_points(
            self.lat_lng, (facility_info.lat, facility_info.lng))/1.609
            

class iCData(models.Model):
    iCRepresentativeName = models.CharField(max_length=200)
    iCLatestCallDate = models.DateField(null=True)
    iCOptOut = models.CharField(max_length=200)
    iCCallBackNeeded = models.CharField(max_length=200)
    iCCallBackDateTime = models.DateTimeField(null=True)
    iCReceivedOtherC19Vaccine = models.CharField(max_length=200)
    iCComments = models.TextField() # Make this a foreign key to a comments model.
    iCInUseBy = models.CharField(max_length=200)
    iCReadyforStudyTeam = models.CharField(max_length=200)
    # Timestamps.
    iCCreatedDateTime = models.DateTimeField(auto_now_add=True)
    iCLastModifiedDateTime = models.DateTimeField(auto_now=True)


class studyTeamData(models.Model):

    # Eligibility choices
    ELIGIBLE = 'EL'
    INELIGIBLE = 'IE'
    INELIGIBLE_OPT_OUT = 'IO'
    UNKNOWN = 'UN'
    eligibility_choices = [
        (ELIGIBLE, 'Eligible'),
        (INELIGIBLE, 'Ineligible'),
        (INELIGIBLE_OPT_OUT,
            'Ineligible - opt out of all studies'),
        (UNKNOWN, 'Unknown')
    ]

    # Enrollment choices.
    ENROLLED = 'EN'
    ENROLLMENT_PENDING = 'EP'
    NOT_ENROLLED = 'NE'
    enrollment_choices = [
        (ENROLLED, 'Enrolled'),
        (ENROLLMENT_PENDING, 'Enrollment pending'),
        (NOT_ENROLLED, 'Not enrolled'),
    ]

    studyTeamOptOut = models.BooleanField(null=True)
    studyTeamEligibilityOutcome = models.CharField(
                                    max_length=2,
                                    choices=eligibility_choices,
                                    default=UNKNOWN)
    studyTeamEnrollmentStatus = models.CharField(
                                    max_length=18,
                                    choices=enrollment_choices,
                                    default=NOT_ENROLLED)
    studyTeamComments = models.TextField()
    studyTeamName = models.CharField(max_length=200)
    # Timestamps.
    studyTeamCreatedDateTime = models.DateTimeField(auto_now_add=True)
    studyTeamLastModifiedDateTime = models.DateTimeField(auto_now=True)


class Record(models.Model):

    # Registry status choices.
    INDEXED = 'IN'
    ICSCREEN = 'IC'
    STUDYTEAM = 'ST'
    registry_status_choices = [
        (INDEXED, 'Indexed'),
        (ICSCREEN, 'iCScreen'),
        (STUDYTEAM, 'studyTeam')
    ]

    submissionId = models.SlugField(max_length=200, unique=True, blank=False)
    createdDateTime = models.DateTimeField(default=dt.datetime(2020, 1, 16))
    registrantData = models.ForeignKey(
                        RegistrantData, on_delete=models.CASCADE)
    iCData = models.ForeignKey(
                        iCData, on_delete=models.CASCADE)
    studyTeamData = models.ForeignKey(
                        studyTeamData, on_delete=models.CASCADE)
    registryStatus = models.CharField(max_length=2,
                                      choices=registry_status_choices,
                                      default=INDEXED)

    # Timestamps.
    recordCreatedDateTime = models.DateTimeField(auto_now_add=True)
    recordLastModifiedDateTime = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'Record {self.registrantData.firstName} {self.registrantData.lastName} ({self.submissionId})'
