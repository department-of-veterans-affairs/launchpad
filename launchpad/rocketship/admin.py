from django.contrib import admin
from rocketship.models import Record, RegistrantData


class RecordAdmin(admin.ModelAdmin):
    # list_filter = ['']
    search_fields = ['submissionId',
                     'registrantData__lastName',
                     'registrantData__phone',
                     'registrantData__email']


class RegistrantAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


admin.site.register(Record, RecordAdmin)

admin.site.register(RegistrantData, RegistrantAdmin)
