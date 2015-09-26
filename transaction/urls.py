# encoding: utf-8
from django.conf.urls import patterns, url
import django
from transaction.views import *;

urlpatterns = patterns(
	'',
	url(r'^files/(?P<pk>\d+)$', transaction_files, name='transaction-files'),
	url(r'^group_form_add', group_form_add, name='group-form-add'),
	url(r'^group_form_edit/(?P<pk>\d+)', group_form_edit, name='group-form-edit'),
	url(r'^field_add', field_add, name='field-add'),
	url(r'^field_edit/(?P<pk>\d+)', field_edit, name='field-edit'),
	url(r'^list_field', list_field, name='list-field'),
	url(r'^list_group_form', list_group_form, name='list-group-form'),
	url(r'^field_delete/(?P<pk>\d+)', field_delete, name='field-delete'),
	url(r'^group_form_delete/(?P<pk>\d+)', group_form_delete, name='group-form-delete'),

	url(r"^create_groupfield", create_groupfield, name="create_groupfield"),
	url(r"^edit_groupfield", edit_groupfield, name="edit_groupfield"),
	url(r"^delete_groupfield", delete_groupfield, name="delete_groupfield"),
	url(r"^groupfield_list", groupfield_list, name="groupfield_list"),
	url(r"^create_form", create_form, name="create_form"),
	url(r"^edit_form", edit_form, name="edit_form"),
	url(r"^delete_form", delete_form, name="delete_form"),
	url(r"^form_list", form_list, name="form_list"),
)
