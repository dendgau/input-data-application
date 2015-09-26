import json
from django import http

from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import resolve
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponse
from django.template.response import TemplateResponse

from allauth.account.utils import get_next_redirect_url

from userprofile.forms import CustomerAdminForm, StaffForm, CustomerStaffForm, BaseSignupForm
from userprofile.models import Company, UserProfile
from userprofile.decorators import permission_access_page_required
from transaction.models import Form, GroupForm
from uploading.models import FileUpload


class JSONResponseMixin(object):
	def render_to_response(self, context):
		return self.get_json_response(self.convert_context_to_json(context))

	def get_json_response(self, content, **http_response_kwargs):
		return http.HttpResponse(
			content,
			content_type='application/json',
			**http_response_kwargs
		)

	def convert_context_to_json(self, context):
		return json.dumps(context)


class StaffFormView(FormView):
	form_class = StaffForm
	redirect_field_name = "next"

	def get_initial(self):
		initial = super(StaffFormView, self).get_initial()
		return initial

	def get_success_url(self):
		ret = (get_next_redirect_url(
			self.request,
			self.redirect_field_name
		) or self.success_url)

		return ret

	def form_valid(self, form):
		return super(StaffFormView, self).form_valid(form)

	@staticmethod
	def get_user_dictionary(form):
		user_info = {
			"username": form.cleaned_data.get("user_name"),
			"email": form.cleaned_data.get("email_address"),
			"password": form.cleaned_data.get("password1"),
			"first_name": form.cleaned_data.get("first_name"),
			"last_name": form.cleaned_data.get("last_name"),
			"is_staff": 1,
		}
		return user_info


class StaffAddFormView(StaffFormView):
	template_name = "user/staff_form.html"
	messages = {
		"user_added": {
			"level": messages.SUCCESS,
			"text": _("New staff account is added")
		},
	}

	def get_initial(self):
		initial = super(StaffAddFormView, self).get_initial()
		initial["action"] = "add"
		return initial

	def form_valid(self, form):
		user = UserProfile.add_new_user(self.get_user_dictionary(form))
		self.success_url = "/user/staff_edit/"+str(user.id)
		if user:
			UserProfile.add_user_profile(user=user)
			messages.add_message(
				self.request,
				messages.SUCCESS,
				"SUCCESS: %s %s - User has been created successfully!" % (user.last_name, user.first_name)
			)

		return super(StaffAddFormView, self).form_valid(form)


class StaffEditFormView(StaffFormView):
	template_name = "user/staff_form.html"
	success_url = ""
	messages = {
		"user_update": {
			"level": messages.SUCCESS,
			"text": _("Updated successfully")
		},
	}

	def get_context_data(self, **kwargs):
		context = super(StaffEditFormView, self).get_context_data(**kwargs)
		context["user_id"] = self.kwargs.get("pk", None)
		return context

	def get_initial(self):
		initial = super(StaffEditFormView, self).get_initial()
		user_id = self.kwargs.get("pk", None)

		try:
			user_info = UserProfile.get_user_info_by_id(user_id)
		except ObjectDoesNotExist:
			raise ObjectDoesNotExist

		initial["user_name"] = user_info.username
		initial["email_address"] = user_info.email
		initial["first_name"] = user_info.first_name
		initial["last_name"] = user_info.last_name
		initial["action"] = "edit"
		initial["user_name_hidden"] = user_info.username
		initial["email_address_hidden"] = user_info.email
		return initial

	def form_valid(self, form):
		user_info = UserProfile.update_user(self.get_user_dictionary(form))
		messages.add_message(
			self.request,
			messages.SUCCESS,
			"SUCCESS: %s %s - User has been updated successfully!" % (user_info.last_name, user_info.first_name)
		)
		return super(StaffEditFormView, self).form_valid(form)

	@staticmethod
	def get_user_dictionary(form):
		user_info = {
			"old_username": form.cleaned_data.get("user_name_hidden"),
			"new_username": form.cleaned_data.get("user_name"),
			"email": form.cleaned_data.get("email_address"),
			"password": form.cleaned_data.get("password1"),
			"first_name": form.cleaned_data.get("first_name"),
			"last_name": form.cleaned_data.get("last_name"),
		}
		return user_info


class CustomerAdminFormView(FormView):
	form_class = CustomerAdminForm
	redirect_field_name = "next"

	def get_initial(self):
		initial = super(CustomerAdminFormView, self).get_initial()
		return initial

	def get_success_url(self):
		ret = (get_next_redirect_url(
			self.request,
			self.redirect_field_name
		) or self.success_url)

		return ret

	def form_valid(self, form):
		return super(CustomerAdminFormView, self).form_valid(form)

	@staticmethod
	def get_user_dictionary(form):
		user_info = {
			"username": form.cleaned_data.get("user_name"),
			"email": form.cleaned_data.get("email_address"),
			"password": form.cleaned_data.get("password1"),
			"first_name": form.cleaned_data.get("first_name"),
			"last_name": form.cleaned_data.get("last_name"),
			"is_staff": 0,
		}
		return user_info

	@staticmethod
	def get_company_dictionary(form):
		company_info = {
			"full_name": form.cleaned_data.get("company_full_name"),
			"short_name": form.cleaned_data.get("company_short_name"),
			"address": form.cleaned_data.get("company_address", None),
			"phone": form.cleaned_data.get("company_phone", None),
			"license_no": form.cleaned_data.get("license_no", None),
			"representative": form.cleaned_data.get("representative", None),
		}
		return company_info


class CustomerAdminAddFormView(CustomerAdminFormView):
	template_name = "user/customer_admin_form.html"
	messages = {
		"user_added": {
			"level": messages.SUCCESS,
			"text": _("New customer account is added")
		},
	}

	def get_initial(self):
		initial = super(CustomerAdminAddFormView, self).get_initial()
		initial["action"] = "add"
		return initial

	def form_valid(self, form):
		user = UserProfile.add_new_user(self.get_user_dictionary(form))
		self.success_url = "customer_admin_edit/"+str(user.id)
		if user:
			company_post = self.get_company_dictionary(form)
			company_before = Company.get_company_with_company_name(company_post["full_name"])

			if company_before:
				messages.add_message(
					self.request,
					messages.WARNING,
					"WARNING: The company name has been existed"
				)

			company = Company.get_or_create_company(company_post)
			UserProfile.add_user_profile(user=user, company=company, is_customer_superadmin=1)
			messages.add_message(
				self.request,
				messages.SUCCESS,
				"SUCCESS: %s %s - User has been created successfully!" % (user.last_name, user.first_name)
			)

		return super(CustomerAdminAddFormView, self).form_valid(form)


class CustomerAdminEditFormView(CustomerAdminFormView):
	template_name = "user/customer_admin_form.html"
	success_url = ""
	messages = {
		"user_update": {
			"level": messages.SUCCESS,
			"text": _("Updated successfully")
		},
	}

	def get_context_data(self, **kwargs):
		context = super(CustomerAdminEditFormView, self).get_context_data(**kwargs)
		context["user_id"] = self.kwargs.get("pk", None)
		return context

	def get_initial(self):
		initial = super(CustomerAdminEditFormView, self).get_initial()
		user_id = self.kwargs.get("pk", None)

		try:
			user_info = UserProfile.get_user_info_by_id(user_id)
		except ObjectDoesNotExist:
			raise ObjectDoesNotExist("Not exist username '%s' in database" % self.kwargs.get("pk", None))

		initial["user_name"] = user_info.username
		initial["email_address"] = user_info.email
		initial["first_name"] = user_info.first_name
		initial["last_name"] = user_info.last_name
		initial["action"] = "edit"
		initial["user_name_hidden"] = user_info.username
		initial["email_address_hidden"] = user_info.email

		company_info = user_info.user_profile.company
		initial["company_full_name"] = company_info.full_name
		initial["company_short_name"] = company_info.short_name
		initial["company_address"] = company_info.address
		initial["company_phone"] = company_info.phone
		initial["license_no"] = company_info.license_no
		initial["representative"] = company_info.representative
		return initial

	def form_valid(self, form):
		user_info_update = self.get_user_dictionary(form)
		UserProfile.update_user(user_info_update)

		user_info = UserProfile.get_user_info_by_username(user_info_update["new_username"])
		company_info_update = self.get_company_dictionary(form)
		company_info_update["id"] = user_info.user_profile.company.id
		Company.update_company_info(company_info_update)
		messages.add_message(
			self.request,
			messages.SUCCESS,
			"SUCCESS: %s %s - User has been updated successfully!" % (user_info.last_name, user_info.first_name)
		)
		return super(CustomerAdminEditFormView, self).form_valid(form)

	@staticmethod
	def get_user_dictionary(form):
		user_info = {
			"old_username": form.cleaned_data.get("user_name_hidden"),
			"new_username": form.cleaned_data.get("user_name"),
			"email": form.cleaned_data.get("email_address"),
			"password": form.cleaned_data.get("password1"),
			"first_name": form.cleaned_data.get("first_name"),
			"last_name": form.cleaned_data.get("last_name")
		}
		return user_info


class CustomerStaffFormView(FormView):
	form_class = CustomerStaffForm
	redirect_field_name = "next"

	def get_initial(self):
		initial = super(CustomerStaffFormView, self).get_initial()
		return initial

	def get_success_url(self):
		ret = (get_next_redirect_url(
			self.request,
			self.redirect_field_name
		) or self.success_url)

		return ret

	def form_valid(self, form):
		return super(CustomerStaffFormView, self).form_valid(form)

	@staticmethod
	def get_user_dictionary(form):
		user_info = {
			"username": form.cleaned_data.get("user_name"),
			"email": form.cleaned_data.get("email_address"),
			"password": form.cleaned_data.get("password1"),
			"first_name": form.cleaned_data.get("first_name"),
			"last_name": form.cleaned_data.get("last_name"),
			"is_staff": 0,
		}
		return user_info


class CustomerStaffAddFormView(CustomerStaffFormView):
	template_name = "user/customer_staff_form.html"
	success_url = "edit"
	messages = {
		"user_added": {
			"level": messages.SUCCESS,
			"text": _("New staff account is added")
		},
	}

	def get_initial(self):
		initial = super(CustomerStaffAddFormView, self).get_initial()
		initial["action"] = "add"
		return initial

	def form_valid(self, form):
		user = UserProfile.add_new_user(self.get_user_dictionary(form))
		self.success_url = "/user/customer_staff_edit/"+str(user.id)
		if user:
			company = self.request.user.user_profile.company

			UserProfile.add_user_profile(user=user, company=company)
			messages.add_message(
				self.request,
				self.messages["user_added"]["level"],
				"SUCCESS: %s %s - User has been created successfully!" % (user.last_name, user.first_name)
			)

		return super(CustomerStaffAddFormView, self).form_valid(form)


class CustomerStaffEditFormView(CustomerStaffFormView):
	template_name = "user/customer_staff_form.html"
	success_url = ""
	messages = {
		"user_update": {
			"level": messages.SUCCESS,
			"text": _("Updated successfully")
		},
	}

	def get_context_data(self, **kwargs):
		context = super(CustomerStaffEditFormView, self).get_context_data(**kwargs)
		context["user_id"] = self.kwargs.get("pk", None)
		return context

	def get_initial(self):
		initial = super(CustomerStaffEditFormView, self).get_initial()
		user_id = self.kwargs.get("pk", None)
		try:
			user_info = UserProfile.get_user_info_by_id(user_id)
		except ObjectDoesNotExist:
			raise ObjectDoesNotExist
		
		initial["user_name"] = user_info.username
		initial["email_address"] = user_info.email
		initial["first_name"] = user_info.first_name
		initial["last_name"] = user_info.last_name
		initial["action"] = "edit"
		initial["user_name_hidden"] = user_info.username
		initial["email_address_hidden"] = user_info.email
		return initial

	def form_valid(self, form):
		user_info = UserProfile.update_user(self.get_user_dictionary(form))
		messages.add_message(
			self.request,
			self.messages["user_update"]["level"],
			"SUCCESS: %s %s - User has been updated successfully!" % (user_info.last_name, user_info.first_name)
		)
		return super(CustomerStaffEditFormView, self).form_valid(form)

	@staticmethod
	def get_user_dictionary(form):
		user_info = {
			"old_username": form.cleaned_data.get("user_name_hidden"),
			"new_username": form.cleaned_data.get("user_name"),
			"email": form.cleaned_data.get("email_address"),
			"password": form.cleaned_data.get("password1"),
			"first_name": form.cleaned_data.get("first_name"),
			"last_name": form.cleaned_data.get("last_name")
		}
		return user_info


class MyProfile(FormView):
	form_class = BaseSignupForm
	template_name = "user/my_profile.html"
	success_url = "/user/profile/"
	messages = {
		"user_update": {
			"level": messages.SUCCESS,
			"text": _("Updated successfully")
		},
	}

	def get_initial(self):
		try:
			initial = super(MyProfile, self).get_initial()
			user_id = self.request.user.id
			user_info = UserProfile.get_user_info_by_id(user_id)
			initial["user_name"] = user_info.username
			initial["email_address"] = user_info.email
			initial["first_name"] = user_info.first_name
			initial["last_name"] = user_info.last_name
			initial["action"] = "edit"
			initial["user_name_hidden"] = user_info.username
			initial["email_address_hidden"] = user_info.email
			return initial
		except ObjectDoesNotExist:
			raise ObjectDoesNotExist

	def form_valid(self, form):
		UserProfile.update_user(self.get_user_dictionary(form))
		messages.add_message(
			self.request,
			self.messages["user_update"]["level"],
			self.messages["user_update"]["text"]
		)
		return super(MyProfile, self).form_valid(form)

	@staticmethod
	def get_user_dictionary(form):
		user_info = {
			"old_username": form.cleaned_data.get("user_name_hidden"),
			"new_username": form.cleaned_data.get("user_name"),
			"email": form.cleaned_data.get("email_address"),
			"password": form.cleaned_data.get("password1", None),
			"first_name": form.cleaned_data.get("first_name"),
			"last_name": form.cleaned_data.get("last_name")
		}
		return user_info


class ListUser(ListView):
	paginate_by = 20
	template_name = "user/list_all_user.html"

	def get_template_names(self):
		if self.request.user.is_superuser:
			return "user/list_all_user.html"
		elif self.request.user.user_profile.is_customer_superadmin:
			return "user/list_customer_staff.html"

	def get_context_data(self, **kwargs):
		context = super(ListUser, self).get_context_data(**kwargs)

		new_object_list = []
		for object in context["object_list"]:
			new_object = {}
			new_object["id"] = object.id
			new_object["username"] = object.username
			new_object["email"] = object.email
			new_object["first_name"] = object.first_name
			new_object["last_name"] = object.last_name

			if not object.is_staff:
				new_object["company"] = object.user_profile.company.full_name
			else:
				new_object["company"] = ""

			new_object["is_staff"] = object.is_staff
			new_object["is_superuser"] = object.is_superuser
			new_object["is_customer_superadmin"] = object.user_profile.is_customer_superadmin
			new_object["date_joined"] = object.date_joined.strftime("%b %d, %Y, %I:%M %p")
			new_object_list.append(new_object)
		context["new_object_list"] = new_object_list
		context["total_item"] = self.object_list.count()
		return context

	def render_to_response(self, context, **kwargs):
		if self.request.is_ajax():
			new_object_list = []
			for object in context["object_list"]:
				new_object = {}
				new_object["id"] = object.id
				new_object["username"] = object.username
				new_object["email"] = object.email
				new_object["first_name"] = object.first_name
				new_object["last_name"] = object.last_name

				if not object.is_staff:
					new_object["company"] = object.user_profile.company.full_name
				else:
					new_object["company"] = ""

				new_object["is_staff"] = object.is_staff
				new_object["is_superuser"] = object.is_superuser
				new_object["is_customer_superadmin"] = object.user_profile.is_customer_superadmin
				new_object["date_joined"] = object.date_joined.strftime("%b %d, %Y, %I:%M %p")
				new_object_list.append(new_object)

			object_json = {}
			object_json["items"] = new_object_list
			object_json["has_next"] = False
			object_json["next_page"] = 0
			if context["page_obj"].has_next():
				object_json["has_next"] = True
				object_json["next_page"] = context["page_obj"].next_page_number()

			return HttpResponse(json.dumps(object_json), content_type='application/json')
		else:
			return super(ListUser, self).render_to_response(context, **kwargs)

	def get_queryset(self):
		query_dict = {}
		if self.request.GET.get("q"):
			query_dict["username__icontains"] = self.request.GET.get("q")

		if self.request.user.is_superuser:
			queryset = User.objects.filter(is_superuser=0, **query_dict).order_by('-id')
		elif self.request.user.user_profile.is_customer_superadmin:
			company_id = self.request.user.user_profile.company.id
			queryset = User.objects.filter(
				is_staff=0,
				user_profile__is_customer_superadmin=0,
				user_profile__company__id=company_id,
				**query_dict
			).order_by('-id')

		return queryset

	def post(self, request, *args, **kwargs):
		if "user_id" in request.POST:
			index_user_delete = self.get_permission_index(User.objects.get(id=request.POST["user_id"]))
			index_user_own = self.get_permission_index(request.user)
			is_delete = True if index_user_own < index_user_delete else False

			if is_delete:
				user_delete = User.objects.get(id=request.POST["user_id"])
				user_delete.delete()
			else:
				return HttpResponse(status=400)

		return HttpResponse(status=200)

	def get_permission_index(self, user):
		if user.is_superuser:
			return 1

		if user.is_staff:
			return 2

		if user.user_profile.is_customer_superadmin:
			return 3

		return 4


class PermissionTemplate(JSONResponseMixin, TemplateView):

	def get(self, request, *args, **kwargs):
		if "action" in request.GET:
			if self.request.user.is_superuser:
				forms_group_json = []
				user_permission_object = {}
				_user = User.objects.get(id=request.GET.get("user"))

				if _user.is_staff:
					forms_group = GroupForm.objects.all()
					forms_permission = _user.user_profile.permission.all()
				else:
					company_id = _user.user_profile.company.id
					group_form_id = [form.groupform.id for form in Form.objects.filter(company__id=company_id)]

					forms_group = GroupForm.objects.filter(id__in=group_form_id)
					forms_permission = _user.user_profile.permission.all()

				for form_permission in forms_permission:
					user_permission_object[form_permission.id] = int(form_permission.id)

				for form_group in forms_group:
					single_object_fg = {}
					single_object_fg["id"] = int(form_group.id)
					single_object_fg["name"] = form_group.name
					forms = Form.objects.filter(groupform__id=int(form_group.id))

					forms_json = []
					items_selected = 0
					for form in forms:
						single_object_f = {}
						single_object_f["id"] = int(form.id)
						single_object_f["name"] = form.name
						single_object_f["group_form_id"] = int(form.groupform.id)
						try:
							get_try = user_permission_object[int(form.id)]
							single_object_f["is_selected"] = True
							single_object_f["is_exist"] = True
							items_selected += 1
						except KeyError:
							single_object_f["is_selected"] = False
							single_object_f["is_exist"] = False
						forms_json.append(single_object_f)

					single_object_fg["forms"] = forms_json
					single_object_fg["items_selected"] = items_selected
					single_object_fg["items_total"] = len(forms_json)
					single_object_fg["is_selected"] = True if len(forms_json) == items_selected else False
					forms_group_json.append(single_object_fg)

				data_response = {
					'forms_group': forms_group_json,
					'permission': user_permission_object
				}
				return self.render_to_response(data_response)
			elif self.request.user.user_profile.is_customer_superadmin:
				forms_group_json = []
				user_permission_object = {}
				user_customer_staff = User.objects.get(id=request.GET.get("user"))

				company_id = user_customer_staff.user_profile.company.id
				group_form_id = [form.groupform.id for form in Form.objects.filter(company__id=company_id)]

				forms_group = GroupForm.objects.filter(id__in=group_form_id)
				forms_permission = user_customer_staff.user_profile.permission.all()

				for form_permission in forms_permission:
					user_permission_object[form_permission.id] = int(form_permission.id)

				for form_group in forms_group:
					single_object_fg = {}
					single_object_fg["id"] = int(form_group.id)
					single_object_fg["name"] = form_group.name
					forms = Form.objects.filter(groupform__id=int(form_group.id), company__id=company_id)

					forms_json = []
					items_selected = 0
					for form in forms:
						single_object_f = {}
						single_object_f["id"] = int(form.id)
						single_object_f["name"] = form.name
						single_object_f["group_form_id"] = int(form.groupform.id)
						try:
							get_try = user_permission_object[int(form.id)]
							single_object_f["is_selected"] = True
							single_object_f["is_exist"] = True
							items_selected += 1
						except KeyError:
							single_object_f["is_selected"] = False
							single_object_f["is_exist"] = False
						forms_json.append(single_object_f)

					single_object_fg["forms"] = forms_json
					single_object_fg["items_selected"] = items_selected
					single_object_fg["items_total"] = len(forms_json)
					single_object_fg["is_selected"] = True if len(forms_json) == items_selected else False
					forms_group_json.append(single_object_fg)

				data_response = {
					'forms_group': forms_group_json,
					'permission': user_permission_object
				}
				return self.render_to_response(data_response)
		else:
			return TemplateResponse(request, "user/permission.html", self.get_context_data())

	def post(self, request, *args, **kwargs):
		if "action" in request.POST:
			user_profile = User.objects.get(
				id=request.POST.get("user")
			).user_profile
			new_permissions_json = request.POST["new_permission"]
			new_permissions = json.loads(new_permissions_json)
			for per in new_permissions:
				if per["is_exist"]:
					if per["is_selected"] is False:
						user_profile.permission.remove(Form.objects.get(id=per["id"]))
				else:
					if per["is_selected"] is True:
						user_profile.permission.add(Form.objects.get(id=per["id"]))

		messages.add_message(self.request, messages.SUCCESS, "Updated successfully")
		message = {"success": True}
		return self.render_to_response(message)


from uploading.models import FileTiff
from decimal import *

@csrf_exempt
def get_notify_staff(request):
	user = request.user
	if not user.is_superuser and user.is_staff:
		permissions = user.user_profile.permission.all()
		list_form_id = [permission.id for permission in permissions]
		files_upload = FileUpload.objects.filter(form__id__in=list_form_id).order_by("-upload_date")

		list_file_not_process = []
		for file in files_upload:
			file_tiff = FileTiff.objects.filter(fileupload=file)
			file_tiff_process = FileTiff.objects.filter(
				fileupload=file,
				status=1
			)

			new_object = {}
			if len(file_tiff_process) < len(file_tiff):
				new_object["name"] = file.name
				new_object["link"] = "/processing/input_data?fileupload_id=%s&form_id=%s"%(file.id, file.form.id)
				new_object["file_process"] = "%s/%s Pages" % (len(file_tiff_process), len(file_tiff))
				new_object["progress"] = str(Decimal(len(file_tiff_process))/Decimal(len(file_tiff))*100)
				list_file_not_process.append(new_object)

		return HttpResponse(json.dumps({"items": list_file_not_process}), content_type="application/json")

@csrf_exempt
def get_menu_header(request):
	user = request.user
	json_response = {}
	array_group_form_id = {}

	current_url_name = resolve(request.POST.get("current_path")).url_name
	if user.is_superuser:
		json_response["type"] = "admin"
		json_response["data"] = []
		json_response["current_url_name"] = current_url_name
	elif user.is_staff:
		forms = User.objects.get(
			id=user.id
		).user_profile.permission.all()
		group_forms = []

		for form in forms:
			object_single_gf = {}
			object_single_f = {}
			group_form = GroupForm.objects.get(id=form.groupform.id)
			try:
				index = array_group_form_id[group_form.id]
				object_single_f["id"] = form.id
				object_single_f["name"] = form.name
				group_forms[index]["forms"].append(object_single_f)
			except KeyError:
				object_single_f["id"] = form.id
				object_single_f["name"] = form.name

				object_single_gf["id"] = group_form.id
				object_single_gf["name"] = group_form.name
				object_single_gf["forms"] = []
				object_single_gf["forms"].append(object_single_f)
				group_forms.append(object_single_gf)
				array_group_form_id[group_form.id] = len(group_forms) - 1

		json_response["type"] = "staff"
		json_response["data"] = group_forms
		json_response["current_url_name"] = current_url_name
	else:
		json_response["type"] = "customer_admin" if user.user_profile.is_customer_superadmin else "customer_staff"
		json_response["data"] = []
		json_response["current_url_name"] = current_url_name

	return HttpResponse(json.dumps(json_response), content_type="application/json")


add_staff = permission_access_page_required(StaffAddFormView.as_view())

add_customer_admin = permission_access_page_required(CustomerAdminAddFormView.as_view())

add_customer_staff = permission_access_page_required(CustomerStaffAddFormView.as_view())

edit_staff = permission_access_page_required(StaffEditFormView.as_view())

edit_customer_staff = permission_access_page_required(CustomerStaffEditFormView.as_view())

edit_customer_admin = permission_access_page_required(CustomerAdminEditFormView.as_view())

list_user = permission_access_page_required(ListUser.as_view())
