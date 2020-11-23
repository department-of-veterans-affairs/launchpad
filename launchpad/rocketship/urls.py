from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.index, name='index'),
    path(route='record/', view=views.IndexView.as_view(), name='record_index'),
    path(route='record/<int:pk>/', view=views.DetailView.as_view(),
         name='record_detail'),
    path(route='record/edit/<int:pk>/', view=views.DetailEditView.as_view(),
         name='record_edit_detail'),
    path(route='record/update/<int:pk>/', view=views.update_record,
         name='record_update'),
    ]
