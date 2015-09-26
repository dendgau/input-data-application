import os
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from userprofile.models import Company


class FieldType(models.Model):
	name = models.CharField(_('Field type'), max_length=250)

	def __unicode__(self):
		return self.name


class Field(models.Model):
	label = models.CharField(_('Label'), max_length=250)
	fieldtype = models.ForeignKey("FieldType", null=True, blank=True)
	description = models.TextField(_('Description'), blank=True)
	html = models.TextField(_('HTML'), blank=True)

	def __unicode__(self):
		return self.label

	@classmethod
	def add_field(cls, dict):
		if dict:
			field = Field.objects.create(**dict)
			field.save()
			return field

	@classmethod
	def get_field_by_id(cls, pk):
		return Field.objects.get(id=pk)

	@classmethod
	def update_field(cls, pk, dict):
		if dict:
			field = cls.get_field_by_id(pk)
			field.label = dict["label"]
			field.fieldtype = dict["fieldtype"]
			field.description = dict["description"]
			field.html = dict["html"]
			field.save()
			return field


class GroupFieldField(models.Model):
	index = models.IntegerField(_('Index'), default=0)
	field = models.ForeignKey("Field", null=True, blank=True)
	groupfield = models.ForeignKey("GroupField", null=True, blank=True)

	def __unicode__(self):
		return '%d' % self.index


class GroupField(models.Model):
	name = models.CharField(_('Name'), max_length=250)

	def __unicode__(self):
		return self.name


class FormField(models.Model):
	index = models.IntegerField(_('Index'), default=0)
	field = models.ForeignKey("Field", null=True, blank=True)
	form = models.ForeignKey("Form", null=True, blank=True)

	def __unicode__(self):
		return '%d' % self.index


class FormGroupField(models.Model):
	index = models.IntegerField(_('Index'), default=0)
	groupfield = models.ForeignKey("GroupField", null=True, blank=True)
	form = models.ForeignKey("Form", null=True, blank=True)

	def __unicode__(self):
		return '%d' % self.index


class GroupForm(models.Model):
	name = models.CharField(_('Name'), max_length=250)
	description = models.TextField(_('Description'), blank=True)
	html = models.TextField(_('HTML content'), blank=True)
	# icon = models.CharField(_('File path'), max_length=250, blank=True)
	icon = models.ImageField(_('File path'), blank=True, upload_to='icon/%d/%m/%Y')

	def __unicode__(self):
		return self.name

	@classmethod
	def get_group_form_by_id(cls, pk):
		return GroupForm.objects.get(id=pk)

	@classmethod
	def add_group_form(cls, dict):
		if dict:
			group_form = GroupForm.objects.create(**dict)
			group_form.save()
			return group_form

	@classmethod
	def update_group_form(cls, pk, dict):
		if dict:
			group_form = cls.get_group_form_by_id(pk)
			group_form.name = dict["name"]
			group_form.description = dict["description"]
			group_form.html = dict["html"]
			group_form.icon = dict["icon"]
			group_form.save()
			return group_form


class Form(models.Model):
	name = models.CharField(_('Name'), max_length=250)
	company = models.ForeignKey("userprofile.Company", null=True, blank=True)
	groupform = models.ForeignKey("GroupForm", null=True, blank=True)

	def __unicode__(self):
		return self.name
