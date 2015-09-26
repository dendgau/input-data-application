# encoding: utf-8
from django.conf.urls import patterns, url
from uploading.views import (
	upload_new, upload_delete, upload_edit, upload_view, upload_history
)
from django.views.generic.base import TemplateView
from website import settings

urlpatterns = patterns(
	'',
	url(r'^new/$', upload_new, name='upload-new'),
	url(r'^delete/(?P<pk>\d+)$', upload_delete, name='upload-delete'),
	url(r'^edit/(?P<pk>\d+)$', upload_edit, name='upload-edit'),
	url(r'^view/$', upload_view, name='upload-view'),
	url(r'^history/$', upload_history, name='upload-history'),
)

# if settings.DEBUG:
# 	urlpatterns += patterns(
# 		'',
# 		url(r'^400/$', TemplateView.as_view(template_name='400.html')),
# 		url(r'^500/$', TemplateView.as_view(template_name='500.html')),
# 	)
