""" Contains serializers to output the study team csvs """

from rest_framework import serializers

from rocketship.models import Gender, RaceEthnicity, Veteran, HealthHistory, \
EmploymentStatus, Transportation, Record, RegistrantData


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields =  [field.name for field in Gender._meta.get_fields() if field.name not in ['registrantdata', 'id']]

class EthnicitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RaceEthnicity
        fields = [field.name for field in RaceEthnicity._meta.get_fields() if field.name not in ['registrantdata', 'id']]

class VeteranSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veteran
        fields = [field.name for field in Veteran._meta.get_fields() if field.name not in ['registrantdata', 'id']]

class HealthHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthHistory
        fields = [field.name for field in HealthHistory._meta.get_fields() if field.name not in ['registrantdata', 'id']]

class EmploymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentStatus
        fields = [field.name for field in EmploymentStatus._meta.get_fields() if field.name not in ['registrantdata', 'id']]

class TransportationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transportation
        fields = [field.name for field in Transportation._meta.get_fields() if field.name not in ['registrantdata', 'id']]

class RegistrantSerializer(serializers.ModelSerializer):
    GENDER = GenderSerializer(many=False, read_only=True)
    RACE_ETHNICITY = EthnicitySerializer(many=False, read_only=True)
    VETERAN = VeteranSerializer(many=False, read_only=True)
    HEALTH_HISTORY = HealthHistorySerializer(many=False, read_only=True)
    EMPLOYMENT_STATUS = EmploymentStatusSerializer(many=False, read_only=True)
    TRANSPORTATION = TransportationSerializer(many=False, read_only=True)
    class Meta:
        model = RegistrantData
        fields = [field.name for field in RegistrantData._meta.get_fields() if field.name not in ['record', 'id', 'formData', 'facilities_w_in_100_mi']] + ['age', 'state', 'timezone']

class RecordSerializer(serializers.ModelSerializer):
    registrantData = RegistrantSerializer(many=False, read_only=True)
    class Meta:
        model = Record
        fields = [field.name for field in Record._meta.get_fields() if field.name not in ['id']] 
