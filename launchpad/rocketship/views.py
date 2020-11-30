import os
import mimetypes
from wsgiref.util import FileWrapper

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required

from rocketship.models import Record


@login_required(login_url='/accounts/login/')
def index(request):
    return HttpResponse('Hello world, you are at the rocketship index.')


@login_required(login_url='/accounts/login/')
def files_list(request):
    test_dir = str(settings.BASE_DIR) + "/rocketship/test_data"
    return render(request,
        'files_list.html',
        {'total_files': os.listdir(test_dir),
        'path': 'test_data'}
    )


@login_required(login_url='/accounts/login/')
def download(request, file_name):
    file_path = str(settings.BASE_DIR) + "/rocketship/test_data/" + file_name
    file_wrapper = FileWrapper(open(file_path,'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    return response


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
