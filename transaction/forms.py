from django.forms import ModelForm
from .models import GroupForm, Field


class GroupFormForm(ModelForm):
	class Meta:
		model = GroupForm

	def __init__(self, *args, **kwargs):
		super(GroupFormForm, self).__init__(*args, **kwargs)
		for field in self.base_fields.values():
			field.widget.attrs['placeholder'] = field.label


class FieldForm(ModelForm):
	class Meta:
		model = Field

	def __init__(self, *args, **kwargs):
		super(FieldForm, self).__init__(*args, **kwargs)
		for field in self.base_fields.values():
			field.widget.attrs['placeholder'] = field.label
