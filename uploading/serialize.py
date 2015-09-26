# encoding: utf-8
import mimetypes
import re
import datetime
from django.core.urlresolvers import reverse
from uploading.models import FileUpload


def order_name(name):
	name = re.sub(r'^.*/', '', name)
	if len(name) <= 40:
		return name
	return name[:10] + "..." + name[-7:]

def serialize(instance, file_attr='file'):
	obj = getattr(instance, file_attr)
	now = datetime.datetime.now()
	if instance.upload_date.year == now.year \
		and instance.upload_date.month == now.month \
		and instance.upload_date.day == now.day:
		DATE_FORMAT = "Today"
	else:
		DATE_FORMAT = "%d-%m-%Y"
	TIME_FORMAT = "%H:%M"

	a = False if instance.process_date is None else True
	return {
		'url': obj.url,
		'name': order_name(obj.instance.name),
		'type': mimetypes.guess_type(obj.path)[0] or 'image/png',
		'thumbnailUrl': obj.url,
		'size': obj.size,
		'note': obj.instance.note,
		'uploadDate': instance.upload_date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)),
		'isProcess': False if instance.process_date is None else True,
		'form': instance.form.name,
		'editUrl': reverse('upload-edit', args=[instance.pk]),
		'deleteUrl': reverse('upload-delete', args=[instance.pk]),
		'deleteType': 'DELETE',
	}


