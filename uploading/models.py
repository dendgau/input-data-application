import os
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from transaction.models import *
from django.conf import settings

from PyPDF2 import PdfFileReader
from wand.image import Image


def get_image_path(instance, file_name):
	now = datetime.datetime.now()
	return os.path.join(
		'pdf',
		str(instance.user_upload.username),
		now.strftime("%Y%m%d"), file_name)


class FileUpload(models.Model):
	name = models.CharField(_('Name'), max_length=500, blank=True)
	file = models.FileField(_('File'), upload_to=get_image_path)
	note = models.TextField(_('Note'), blank=True)
	form = models.ForeignKey(Form, null=True, blank=True)	
	
	upload_date = models.DateTimeField(_('Upload date'), auto_now_add=True)
	user_upload = models.ForeignKey(User, related_name='user_upload', null=True, blank=True)

	process_date = models.DateTimeField(_('Process date'), null=True, blank=True)
	user_process = models.ForeignKey(User, related_name='user_process', null=True, blank=True)

	def __unicode__(self):
		return self.file.name

	@models.permalink
	def get_absolute_url(self):
		return ('upload-new', )

	def save(self, *args, **kwargs):
		file_name_element = self.file.name.split("/")
		file_name_pdf = file_name_element[len(file_name_element) - 1]
		file_name = file_name_pdf.split(".")

		del file_name[len(file_name)-1]
		file_name = " ".join(file_name)

		self.slug = slugify(file_name)
		if not self.name:
			self.name = file_name
		super(FileUpload, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		"""delete -- Remove to leave file."""
		self.file.delete(False)
		super(FileUpload, self).delete(*args, **kwargs)
	
	#for split pdf to images
	def convert_to_png(self, width=0, height=0):
		self.__convert_to_img__(width, height, 'png')

	def convert_to_jpg(self, width=0, height=0):
		self.__convert_to_img__(width, height, 'jpg')

	def __convert_to_img__(self, width, height, format='jpg'):
		size = ''
		if width and height:
			size = '_' + str(width) + 'x' + str(height) + 'px'
		
		full_tiff_file_url = self.file.name   #pdf/test3/20150712/pil_c75tnZc.pdf
		tiff_file_url_subs = full_tiff_file_url.split('.')
		tiff_file_url = settings.MEDIA_URL + tiff_file_url_subs[0] + '/'

		filepath = self.file.url 
		substrings = filepath.split('/')
		pdf_name = substrings[len(substrings) - 1]
		pdf_substrings = pdf_name.split('.')
		tiff_folder = pdf_substrings[0]
		tiff_path = filepath.replace(pdf_name,"")
		
		output_dir = os.path.join(settings.PACKAGE_ROOT + tiff_path + tiff_folder + '/')
		os.mkdir(output_dir)
		
		input_file = PdfFileReader(file(os.path.join(settings.PACKAGE_ROOT + filepath), 'rb'))
		for i in range(input_file.getNumPages()):
			with Image(filename = os.path.join(settings.PACKAGE_ROOT + filepath) + '[' + str(i) + ']') as img:
				if len(size) > 0:
					img.resize(width, height)
				img.format = format
				img.save(filename = output_dir + str(i) + '.' + format)
				filetiff = FileTiff(name = str(i), path = tiff_file_url + str(i) + '.' + format, status = 0, page_index = i, fileupload = self)
				filetiff.save()
				
#three most heavy tables:  FormFieldValue, FileUploadGroupField, FileUploadGroupFieldFieldValue 
#because all data will be saved to these tables
class FormFieldValue(models.Model):
	value = models.CharField(_('Field value'), max_length=500)
	fileupload = models.ForeignKey("FileUpload", null=True, blank=True)
	formfield = models.ForeignKey(FormField, null=True, blank=True)
	
	def __unicode__(self):
		return self.value


class FileUploadGroupField(models.Model):
	fileupload = models.ForeignKey("FileUpload", null=True, blank=True)
	groupfield = models.ForeignKey(GroupField, null=True, blank=True)
	
	def __unicode__(self):
		return '%d' % self.id	

#this table for counting how many items in an Invoice/pdf
#should check this table to see it can be 2 row with the same data (differ in ID of each row)
#because its just for counting No. of item so FileUpload_Id and GroupField_Id will be the same
#already, can insert to row with same data except Id => working well
class FileUploadGroupFieldFieldValue(models.Model):
	value = models.CharField(_('Field value'), max_length=500)
	fileuploadgroupfield = models.ForeignKey("FileUploadGroupField", null=True, blank=True)
	groupfieldfield = models.ForeignKey(GroupFieldField, null=True, blank=True)
	
	def __unicode__(self):
		return self.value

class WarningUpload(models.Model):
	content_error = models.TextField(_('Warning'))
	fileupload = models.ForeignKey(FileUpload, null=True, blank=True)

	def __unicode__(self):
		return self.content_error


class FileTiff(models.Model):
	name = models.CharField(_('Name'), max_length=250)
	path = models.CharField(_('File path'), max_length=250, blank=True)
	status = models.IntegerField(_('Status'), default=0) #this field to check if the file have been processed or not
	page_index = models.IntegerField(_('Page index'), default=0)

	fileupload = models.ForeignKey(FileUpload)

	def __unicode__(self):
		return self.name