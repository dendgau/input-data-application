from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from allauth.account import app_settings, adapter
from userprofile.models import UserProfile


class PasswordField(forms.CharField):

	def __init__(self, *args, **kwargs):
		render_value = kwargs.pop(
			'render_value',
			app_settings.PASSWORD_INPUT_RENDER_VALUE
		)
		kwargs['widget'] = forms.PasswordInput(
			render_value=render_value,
			attrs={
				'placeholder': _(kwargs.get("label"))
			}
		)
		super(PasswordField, self).__init__(*args, **kwargs)


class SetPasswordField(PasswordField):

	def clean(self, value):
		value = super(SetPasswordField, self).clean(value)
		value = adapter.get_adapter().clean_password(value)
		return value


class CompanyForm(forms.Form):

	company_full_name = forms.CharField(
		label=_("Company name"),
		min_length=3,
		max_length=100,
		widget=forms.TextInput(
			attrs={
				'placeholder': _('Company name'),
			}
		),
		error_messages={'required': 'Company name is required'}
	)
	company_short_name = forms.CharField(
		label=_("Company short name"),
		min_length=3,
		max_length=20,
		widget=forms.TextInput(
			attrs={
				'placeholder': _('Company short name'),
			}
		),
		error_messages={'required': 'Company short name is required'}

	)
	company_address = forms.CharField(
		label=_("Company address"),
		max_length=50,
		widget=forms.Textarea(
			attrs={
				'placeholder': _('Company address'),
			}
		),
		required=False
	)
	company_phone = forms.CharField(
		label=_("Phone No"),
		max_length=30,
		widget=forms.TextInput(
			attrs={
				'placeholder': _('Phone number'),
			}
		),
		required=False
	)
	license_no = forms.CharField(
		label=_("License No"),
		max_length=30,
		widget=forms.TextInput(
			attrs={
				'placeholder': _('License No'),
			}
		),
		required=False
	)
	representative = forms.CharField(
		label=_("Representative"),
		max_length=30,
		widget=forms.TextInput(
			attrs={
				'placeholder': _('Representative'),
			}
		),
		required=False
	)

class BaseSignupForm(forms.Form):

	user_name = forms.CharField(
		label=_("Username"),
		max_length=100,
		min_length=3,
		widget=forms.TextInput(
			attrs={
				'placeholder': _('Username'),
				'autofocus': 'autofocus'
			}
		),
		error_messages={'required': 'Username is required'}
	)
	email_address = forms.EmailField(
		label=_("Email"),
		widget=forms.TextInput(
			attrs={
				'type': 'email',
				'placeholder': _('E-mail address')
			}
		),
		error_messages={'required': 'E-mail is required'}
	)
	first_name = forms.CharField(
		label=_("First name"),
		max_length=100,
		min_length=3,
		widget=forms.TextInput(
			attrs={'placeholder': _('First name')}
		),
		error_messages={'required': 'First name is required'}
	)
	last_name = forms.CharField(
		label=_("Last name"),
		max_length=100,
		min_length=3,
		widget=forms.TextInput(
			attrs={'placeholder': _('Last name')}
		),
		error_messages={'required': 'Last name is required'}
	)
	action = forms.CharField(
		max_length=50,
		widget=forms.HiddenInput(),
		required=False
	)
	user_name_hidden = forms.CharField(
		max_length=100,
		widget=forms.HiddenInput(),
		required=False
	)
	email_address_hidden = forms.CharField(
		max_length=100,
		widget=forms.HiddenInput(),
		required=False
	)

	def clean(self):
		super(BaseSignupForm, self).clean()

		if "user_name" in self.cleaned_data:
			if self.cleaned_data["user_name"] != self.cleaned_data["user_name_hidden"]:
				if UserProfile.check_user_exist(self.cleaned_data["user_name"]):
					errors = self._errors.setdefault("user_name", ErrorList())
					errors.append(_('Username "%s" is already in use.' % self.cleaned_data["user_name"]))

		if "email_address" in self.cleaned_data:
			if self.cleaned_data["email_address"] != self.cleaned_data["email_address_hidden"]:
				if UserProfile.check_email_exist(self.cleaned_data["email_address"]):
					errors = self._errors.setdefault("email_address", ErrorList())
					errors.append(_('E-mail address "%s" is already in use.' % self.cleaned_data["email_address"]))


class CustomerAdminForm(BaseSignupForm, CompanyForm):

	password1 = SetPasswordField(
		label=_("Password"),
		render_value=True,
		error_messages={'required': 'Password is required'}
	)
	password2 = PasswordField(
		label=_("Re-password"),
		error_messages={'required': 'Re-password is required'}
	)

	def __init__(self, *args, **kwargs):
		super(CustomerAdminForm, self).__init__(*args, **kwargs)
		if not app_settings.SIGNUP_PASSWORD_VERIFICATION:
			del self.fields["password2"]

	def clean(self):
		super(CustomerAdminForm, self).clean()

		# if "user_name" in self.cleaned_data:
		# 	if self.cleaned_data["user_name"] != self.cleaned_data["user_name_hidden"]:
		# 		if UserProfile.check_user_exist(self.cleaned_data["user_name"]):
		# 			errors = self._errors.setdefault("user_name", ErrorList())
		# 			errors.append(_('Username "%s" is already in use.' % self.cleaned_data["user_name"]))
		#
		# if "email_address" in self.cleaned_data:
		# 	if self.cleaned_data["email_address"] != self.cleaned_data["email_address_hidden"]:
		# 		if UserProfile.check_email_exist(self.cleaned_data["email_address"]):
		# 			errors = self._errors.setdefault("email_address", ErrorList())
		# 			errors.append(_('E-mail address "%s" is already in use.' % self.cleaned_data["email_address"]))

		if app_settings.SIGNUP_PASSWORD_VERIFICATION:
			if "password1" in self.cleaned_data \
				and "password2" in self.cleaned_data \
				and self.cleaned_data["password1"] != self.cleaned_data["password2"]:
					errors = self._errors.setdefault("password2", ErrorList())
					errors.append(_("You must type the same password each time."))
					# raise forms.ValidationError(_("You must type the same password each time."))
			elif self.cleaned_data["action"] == "edit"\
				and "password1" not in self.changed_data \
				and "password2" not in self.changed_data:
				del self.errors["password2"]
				del self.errors["password1"]

		return self.cleaned_data


class StaffForm(BaseSignupForm):
	password1 = SetPasswordField(
		label=_("Password"),
		render_value=True,
		error_messages={'required': 'Password is required'}
	)
	password2 = PasswordField(
		label=_("Re-password"),
		error_messages={'required': 'Re-password is required'}
	)

	def __init__(self, *args, **kwargs):
		super(StaffForm, self).__init__(*args, **kwargs)
		if not app_settings.SIGNUP_PASSWORD_VERIFICATION:
			del self.fields["password2"]

	def clean(self):
		super(StaffForm, self).clean()

		# if "user_name" in self.cleaned_data:
		# 	if self.cleaned_data["user_name"] != self.cleaned_data["user_name_hidden"]:
		# 		if UserProfile.check_user_exist(self.cleaned_data["user_name"]):
		# 			errors = self._errors.setdefault("user_name", ErrorList())
		# 			errors.append(_('Username "%s" is already in use.' % self.cleaned_data["user_name"]))
		#
		# if "email_address" in self.cleaned_data:
		# 	if self.cleaned_data["email_address"] != self.cleaned_data["email_address_hidden"]:
		# 		if UserProfile.check_email_exist(self.cleaned_data["email_address"]):
		# 			errors = self._errors.setdefault("email_address", ErrorList())
		# 			errors.append(_('E-mail address "%s" is already in use.' % self.cleaned_data["email_address"]))

		if app_settings.SIGNUP_PASSWORD_VERIFICATION:
			if "password1" in self.cleaned_data \
				and "password2" in self.cleaned_data \
				and self.cleaned_data["password1"] != self.cleaned_data["password2"]:
					errors = self._errors.setdefault("password2", ErrorList())
					errors.append(_("You must type the same password each time."))
					# raise forms.ValidationError(_("You must type the same password each time."))
			elif self.cleaned_data["action"] == "edit"\
				and "password1" not in self.changed_data \
				and "password2" not in self.changed_data:
				del self.errors["password2"]
				del self.errors["password1"]

		return self.cleaned_data


class CustomerStaffForm(BaseSignupForm):
	password1 = SetPasswordField(
		label=_("Password"),
		render_value=True,
		error_messages={'required': 'Password is required'}
	)
	password2 = PasswordField(
		label=_("Re-password"),
		error_messages={'required': 'Re-password is required'}
	)

	def __init__(self, *args, **kwargs):
		super(CustomerStaffForm, self).__init__(*args, **kwargs)
		if not app_settings.SIGNUP_PASSWORD_VERIFICATION:
			del self.fields["password2"]

	def clean(self):
		super(CustomerStaffForm, self).clean()

		# if "user_name" in self.cleaned_data:
		# 	if self.cleaned_data["user_name"] != self.cleaned_data["user_name_hidden"]:
		# 		if UserProfile.check_user_exist(self.cleaned_data["user_name"]):
		# 			errors = self._errors.setdefault("user_name", ErrorList())
		# 			errors.append(_('Username "%s" is already in use.' % self.cleaned_data["user_name"]))
		#
		# if "email_address" in self.cleaned_data:
		# 	if self.cleaned_data["email_address"] != self.cleaned_data["email_address_hidden"]:
		# 		if UserProfile.check_email_exist(self.cleaned_data["email_address"]):
		# 			errors = self._errors.setdefault("email_address", ErrorList())
		# 			errors.append(_('E-mail address "%s" is already in use.' % self.cleaned_data["email_address"]))

		if app_settings.SIGNUP_PASSWORD_VERIFICATION:
			if "password1" in self.cleaned_data \
				and "password2" in self.cleaned_data \
				and self.cleaned_data["password1"] != self.cleaned_data["password2"]:
					errors = self._errors.setdefault("password2", ErrorList())
					errors.append(_("You must type the same password each time."))
					# raise forms.ValidationError(_("You must type the same password each time."))
			elif self.cleaned_data["action"] == "edit"\
				and "password1" not in self.changed_data \
				and "password2" not in self.changed_data:
				del self.errors["password2"]
				del self.errors["password1"]

		return self.cleaned_data
