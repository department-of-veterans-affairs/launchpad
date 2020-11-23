from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rocketship.forms import RecordForm
from rocketship.models import Record
from django.views import generic
from django.urls import reverse


def index(request):
    return HttpResponse('Hello world, you are at the rocketship index.')


class IndexView(generic.ListView):
    template_name = 'record/index.html'
    context_object_name = 'record_index_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Record.objects.order_by('-registrantData__lastName')[:10]


class DetailView(generic.DetailView):
    model = Record
    slug_field = 'submissionId'
    template_name = 'record/detail.html'
    edit_mode = 'disabled'


class DetailEditView(generic.DetailView):
    model = Record
    slug_field = 'submissionId'
    template_name = 'record/detail.html'
    edit_mode = ''


def update_record(request, pk):
    target = Record.objects.get(pk=pk)
    registrantData = getattr(target, 'registrantData')
    iCData = getattr(target, 'iCData')

    # Digest form data.
    multi_select_update_material = {}
    simple_update_material = {}
    ic_data_update_material = {}
    for item in request.POST.items():

        if item[0] == 'csrfmiddlewaretoken':
            continue

        if '::' in item[0]:
            category, type = item[0].split('::')
            if 'iCData' in item[0]:
                ic_data_update_material[type] = item[1]
                continue
            try:
                multi_select_update_material[category].append(type)
            except KeyError:
                multi_select_update_material[category] = [type]

        else:
            simple_update_material[item[0]] = item[1]

    # Work through each multiselect category (e.g. health history, gender...)
    for category in multi_select_update_material:
        sub_object = getattr(target.registrantData, category)

        # Get all fields from multiselect category object and null them out
        nulled_data = {attribute.name: None for attribute in
                        sub_object._meta.fields if attribute.name != 'id'}

        # Repopulate multiselect category object with only "True"s from form
        # data
        for type in multi_select_update_material[category]:
            nulled_data[type] = True

        # Set attributes using re-populated data
        new_data = nulled_data
        for attr, value in new_data.items():
            setattr(sub_object, attr, value)

        # Save changes
        sub_object.save()

    for attribute, value in simple_update_material.items():
        setattr(registrantData, attribute, value)

    for attribute, value in ic_data_update_material.items():
        setattr(iCData, attribute, value)
    print(ic_data_update_material)
    registrantData.save()
    iCData.save()

    return HttpResponseRedirect(reverse('record_detail', args=(pk,)))
