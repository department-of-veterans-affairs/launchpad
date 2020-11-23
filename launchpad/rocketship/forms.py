from django.forms import ModelForm
from rocketship.models import Record


class RecordForm(ModelForm):
    class Meta:
        model = Record
        fields = ['submissionId']
