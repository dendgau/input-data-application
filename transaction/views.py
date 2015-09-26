import json
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView
from django.views.generic import ListView, DeleteView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from operator import itemgetter
import datetime
from decimal import *

from uploading.models import *
from transaction.models import *
from userprofile.models import *
from .forms import GroupFormForm, FieldForm
from allauth.account.utils import get_next_redirect_url
from userprofile.decorators import permission_access_page_required
from uploading.tools import filesizeformat


class GroupFormView(FormView):
	form_class = GroupFormForm
	redirect_field_name = "next"

	def get_initial(self):
		initial = super(GroupFormView, self).get_initial()
		return initial

	def get_success_url(self):
		ret = (get_next_redirect_url(
			self.request,
			self.redirect_field_name
		) or self.success_url)

		return ret

	def form_valid(self, form):
		return super(GroupFormView, self).form_valid(form)

	@staticmethod
	def get_group_form_dictionary(form):
		group_form = {
			"name": form.cleaned_data.get("name"),
			"description": form.cleaned_data.get("description"),
			"html": form.cleaned_data.get("html"),
			"icon": form.cleaned_data.get("icon"),
		}
		return group_form


class GroupFormAddView(GroupFormView):
	template_name = "transaction/group_form_form.html"
	messages = {
		"user_added": {
			"level": messages.SUCCESS,
			"text": _("New group form is added")
		},
	}

	def get_context_data(self, **kwargs):
		context = super(GroupFormAddView, self).get_context_data(**kwargs)
		context["action"] = "add"
		return context

	def form_valid(self, form):
		group_form = GroupForm.add_group_form(self.get_group_form_dictionary(form))
		self.success_url = "/transaction/group_form_edit/"+str(group_form.id)
		if group_form:
			messages.add_message(
				self.request,
				self.messages["user_added"]["level"],
				"SUCCESS: %s - GroupForm has been created successfully!" % (group_form.name)
			)

		return super(GroupFormAddView, self).form_valid(form)


class GroupFormEditView(GroupFormView):
	template_name = "transaction/group_form_form.html"
	messages = {
		"user_added": {
			"level": messages.SUCCESS,
			"text": _("Updated success")
		},
	}

	def delete(self, request, *args, **kwargs):
		if self.request.is_ajax():
			group_form = GroupForm.objects.get(id=self.kwargs.get('pk'))
			group_form.icon.delete()
			return HttpResponse(status=202)

	def get_context_data(self, **kwargs):
		context = super(GroupFormEditView, self).get_context_data(**kwargs)
		group_form = GroupForm.objects.get(id=self.kwargs.get('pk'))
		context["groupform_id"] = group_form.id
		context["action"] = "edit"
		if group_form.icon:
			context["icon_path"] = group_form.icon
		return context

	def get_initial(self):
		try:
			initial = super(GroupFormEditView, self).get_initial()
			group_form_id = self.kwargs.get("pk", None)
			group_form = GroupForm.get_group_form_by_id(group_form_id)
			initial["name"] = group_form.name
			initial["description"] = group_form.description
			initial["html"] = group_form.html
			initial["icon"] = group_form.icon
			return initial
		except ObjectDoesNotExist:
			raise ObjectDoesNotExist

	def form_valid(self, form):
		group_form_id = self.kwargs.get("pk", None)
		group_form = GroupForm.objects.get(id=self.kwargs.get('pk'))
		if group_form_id is not None:
			if group_form.icon and "icon" in form.changed_data:
				group_form.icon.delete()
			group_form = GroupForm.update_group_form(group_form_id, self.get_group_form_dictionary(form))
			messages.add_message(
				self.request,
				self.messages["user_added"]["level"],
				"SUCCESS: %s - GroupForm has been updated successfully!" % (group_form.name)
			)
			self.success_url = "/transaction/group_form_edit/"+str(group_form_id)

		return super(GroupFormEditView, self).form_valid(form)


class FilesProcessView(ListView):
	model = FileUpload
	paginate_by = 20
	template_name = "transaction/list_file_form.html"

	def get_context_data(self, **kwargs):
		context = super(FilesProcessView, self).get_context_data(**kwargs)
		form_info = Form.objects.get(id=self.kwargs.get("pk", None))
		form_name = form_info.name
		group_form_name = form_info.groupform.name

		new_object_list = []
		for object in context["object_list"]:
			new_object = {}
			new_object["id"] = object.id
			new_object["name"] = object.name
			new_object["file"] = object.file
			new_object["note"] = object.note.replace("\r\n", " ")
			new_object["form"] = object.form
			new_object["upload_date"] = object.upload_date.strftime("%b %d, %Y, %I:%M %p")
			new_object["user_process"] = object.user_process
			new_object["process_date"] = ""
			if object.process_date:
				new_object["process_date"] = object.process_date.strftime("%b %d, %Y, %I:%M %p")

			file_tiff = FileTiff.objects.filter(fileupload=object)
			file_tiff_process = FileTiff.objects.filter(
				fileupload=object,
				status=1
			)

			if len(file_tiff) > 0:
				new_object["file_process"] = "%s/%s Pages" % (len(file_tiff_process), len(file_tiff))
				new_object["progress"] = Decimal(len(file_tiff_process))/Decimal(len(file_tiff))*100
				new_object["is_finish_process"] = True if len(file_tiff_process) == len(file_tiff) else False
				new_object["is_start_process"] = True if len(file_tiff_process) > 0 else False
				new_object["is_exist_file_tiff"] = True
			else:
				new_object["file_process"] = "There are not any tiff file"
				new_object["progress"] = ""
				new_object["is_finish_process"] = False
				new_object["is_start_process"] = False
				new_object["is_exist_file_tiff"] = False

			new_object_list.append(new_object)

		context["new_object_list"] = new_object_list
		context['breadcrumb'] = [group_form_name, form_name]
		context["form_name"] = form_name
		context['form_id'] = form_info.id
		return context

	def get_queryset(self):
		query_dict = {}
		if self.request.GET.get("q"):
			query_dict["name__icontains"] = self.request.GET.get("q")

		user = self.request.user
		forms_id = [str(form.id) for form in user.user_profile.permission.all()]
		form_id = str(self.kwargs.get("pk", None))
		set_form_id = 0

		try:
			if form_id in forms_id:
				set_form_id = form_id

			queryset = FileUpload.objects.filter(
				form__id=set_form_id,
				**query_dict
			).order_by("-upload_date")
		except ValueError:
			raise ValueError("You do not have permissions to access this form")

		return queryset

	def render_to_response(self, context, **kwargs):
		if self.request.is_ajax():
			object_json = {}
			object_json["items"] = new_object_list = []

			for object in context["object_list"]:
				new_object = {}
				new_object["id"] = object.id
				new_object["name"] = object.name
				new_object["file"] = object.file.name
				new_object["size"] = filesizeformat(object.file.size)
				new_object["note"] = object.note.replace("\r\n", " ")
				new_object["form"] = object.form.name
				new_object["form_id"] = object.form.id
				new_object["upload_date"] = object.upload_date.strftime("%b %d, %Y, %I:%M %p")

				new_object["process_date"] = ""
				if object.process_date:
					new_object["process_date"] = object.process_date.strftime("%b %d, %Y, %I:%M %p")

				file_tiff = FileTiff.objects.filter(fileupload=object)
				file_tiff_process = FileTiff.objects.filter(
					fileupload=object,
					status=1
				)
				if len(file_tiff) > 0:
					new_object["file_process"] = "%s/%s Pages" % (len(file_tiff_process), len(file_tiff))
					new_object["progress"] = int(Decimal(len(file_tiff_process))/Decimal(len(file_tiff))*100)
					new_object["is_finish_process"] = True if len(file_tiff_process) == len(file_tiff) else False
					new_object["is_start_process"] = True if len(file_tiff_process) > 0 else False
					new_object["is_exist_file_tiff"] = True
				else:
					new_object["file_process"] = "There are not any tiff file"
					new_object["progress"] = ""
					new_object["is_finish_process"] = False
					new_object["is_start_process"] = False
					new_object["is_exist_file_tiff"] = False

				new_object_list.append(new_object)

			object_json["items"] = new_object_list
			object_json["has_next"] = False
			object_json["next_page"] = 0
			if context["page_obj"].has_next():
				object_json["has_next"] = True
				object_json["next_page"] = context["page_obj"].next_page_number()

			return HttpResponse(json.dumps(object_json), content_type='application/json')
		else:
			return super(FilesProcessView, self).render_to_response(context, **kwargs)


transaction_files = permission_access_page_required(FilesProcessView.as_view())

group_form_add = permission_access_page_required(GroupFormAddView.as_view())

group_form_edit = permission_access_page_required(GroupFormEditView.as_view())


class FieldView(FormView):
	form_class = FieldForm
	redirect_field_name = "next"

	def get_initial(self):
		initial = super(FieldView, self).get_initial()
		return initial

	def get_success_url(self):
		ret = (get_next_redirect_url(
			self.request,
			self.redirect_field_name
		) or self.success_url)

		return ret

	def form_valid(self, form):
		return super(FieldView, self).form_valid(form)

	@staticmethod
	def get_field_dictionary(form):
		field = {
			"label": form.cleaned_data.get("label"),
			"fieldtype": form.cleaned_data.get("fieldtype"),
			"description": form.cleaned_data.get("description"),
			"html": form.cleaned_data.get("html"),
		}
		return field


class FieldAddView(FieldView):
	template_name = "transaction/field_form.html"
	messages = {
		"user_added": {
			"level": messages.SUCCESS,
			"text": _("New field has been created successfully!")
		},
	}

	def get_context_data(self, **kwargs):
		context = super(FieldAddView, self).get_context_data(**kwargs)
		context["field_id"] = self.kwargs.get("pk", None)
		context["action"] = "add"
		return context

	def form_valid(self, form):
		field = Field.add_field(self.get_field_dictionary(form))
		self.success_url = "/transaction/field_edit/"+str(field.id)
		if field:
			messages.add_message(
				self.request,
				self.messages["user_added"]["level"],
				"SUCCESS: %s - Field has been created successfully!" % (field.label)
			)

		return super(FieldAddView, self).form_valid(form)


class FieldEditView(FieldView):
	template_name = "transaction/field_form.html"
	messages = {
		"user_added": {
			"level": messages.SUCCESS,
			"text": _("New field has been updated successfully!")
		},
	}

	def get_context_data(self, **kwargs):
		context = super(FieldEditView, self).get_context_data(**kwargs)
		context["field_id"] = self.kwargs.get("pk", None)
		context["action"] = "edit"
		return context

	def get_initial(self):
		try:
			initial = super(FieldEditView, self).get_initial()
			field_id = self.kwargs.get("pk", None)
			group_form = Field.get_field_by_id(field_id)
			initial["label"] = group_form.label
			initial["fieldtype"] = group_form.fieldtype
			initial["description"] = group_form.description
			initial["html"] = group_form.html
			return initial
		except ObjectDoesNotExist:
			raise ObjectDoesNotExist

	def form_valid(self, form):
		field_id = self.kwargs.get("pk", None)
		if field_id is not None:
			field = Field.update_field(field_id, self.get_field_dictionary(form))
			messages.add_message(
				self.request,
				self.messages["user_added"]["level"],
				"SUCCESS: %s - Field  has been updated successfully!" % (field.label)
			)
			self.success_url = "/transaction/field_edit/"+str(field_id)

		return super(FieldEditView, self).form_valid(form)


class ListField(ListView):
	paginate_by = 20
	template_name = "transaction/list_field.html"

	def get_queryset(self):
		query_dict = {}
		if self.request.GET.get("q"):
			query_dict["label__icontains"] = self.request.GET.get("q")

		queryset = Field.objects.filter(**query_dict).order_by("-id")
		return queryset

	def get_context_data(self, **kwargs):
		context = super(ListField, self).get_context_data(**kwargs)
		context["total_item"] = self.object_list.count()
		return context

	def render_to_response(self, context, **kwargs):
		if self.request.is_ajax():
			new_object_list = []
			for object in context["object_list"]:
				new_object = {}
				new_object["id"] = object.id
				new_object["label"] = object.label

				new_object["fieldtype"] = ""
				if object.fieldtype:
					new_object["fieldtype"] = object.fieldtype.name

				new_object["description"] = object.description
				new_object["html"] = object.html
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
			return super(ListField, self).render_to_response(context, **kwargs)


class ListGroupForm(ListView):
	paginate_by = 20
	template_name = "transaction/list_group_form.html"

	def get_queryset(self):
		query_dict = {}
		if self.request.GET.get("q"):
			query_dict["name__icontains"] = self.request.GET.get("q")

		queryset = GroupForm.objects.filter(**query_dict).order_by("-id")
		return queryset

	def get_context_data(self, **kwargs):
		context = super(ListGroupForm, self).get_context_data(**kwargs)
		context["total_item"] = self.object_list.count()
		return context

	def render_to_response(self, context, **kwargs):
		if self.request.is_ajax():
			new_object_list = []
			for object in context["object_list"]:
				new_object = {}
				new_object["id"] = object.id
				new_object["name"] = object.name
				new_object["description"] = object.description
				new_object["html"] = object.html

				new_object["icon"] = ""
				if object.icon:
					new_object["icon"] = object.icon.url

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
			return super(ListGroupForm, self).render_to_response(context, **kwargs)


class FieldDeleteView(DeleteView):
	model = Field

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.delete()
		return HttpResponse(status=200)


class GroupFormDeleteView(DeleteView):
	model = GroupForm

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.delete()
		return HttpResponse(status=200)


field_add = permission_access_page_required(FieldAddView.as_view())

field_edit = permission_access_page_required(FieldEditView.as_view())

list_field = permission_access_page_required(ListField.as_view())

list_group_form = permission_access_page_required(ListGroupForm.as_view())

field_delete = permission_access_page_required(FieldDeleteView.as_view())

group_form_delete = permission_access_page_required(GroupFormDeleteView.as_view())


class GroupFieldList(ListView):
	paginate_by = 20
	template_name = "groupfield_list.html"

	def get_queryset(self):
		query_dict = {}
		if self.request.GET.get("q"):
			query_dict["name__icontains"] = self.request.GET.get("q")

		queryset = GroupField.objects.filter(**query_dict).order_by("-id")
		return queryset

	def get_context_data(self, **kwargs):
		context = super(GroupFieldList, self).get_context_data(**kwargs)
		new_object_list = []
		for object in context["object_list"]:
			new_object = {}
			new_object["id"] = object.id
			new_object["name"] = object.name
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
				new_object["name"] = object.name
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
			return super(GroupFieldList, self).render_to_response(context, **kwargs)


class FormList(ListView):
	paginate_by = 20
	template_name = "form_list.html"

	def get_queryset(self):
		query_dict = {}
		if self.request.GET.get("q"):
			query_dict["name__icontains"] = self.request.GET.get("q")

		queryset = Form.objects.filter(**query_dict).order_by("-id")
		return queryset

	def get_context_data(self, **kwargs):
		context = super(FormList, self).get_context_data(**kwargs)
		context["total_item"] = self.object_list.count()
		return context

	def render_to_response(self, context, **kwargs):
		if self.request.is_ajax():
			new_object_list = []
			for object in context["object_list"]:
				new_object = {}
				new_object["id"] = object.id
				new_object["name"] = object.name
				new_object["company"] = object.company.full_name
				new_object["groupform"] = object.groupform.name
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
			return super(FormList, self).render_to_response(context, **kwargs)


groupfield_list = permission_access_page_required(GroupFieldList.as_view())

form_list = permission_access_page_required(FormList.as_view())


# Create your views here.
@csrf_exempt
def create_groupfield(request):
	if request.method == 'GET': #populate form for user to create groupfield
		current_user = request.user
		is_active = current_user.is_active
		is_superuser = current_user.is_superuser
		if(is_active and is_superuser):
			field_list = []
			fields = Field.objects.all()
			for field in fields:
				dic = {}
				dic["id"] = field.id
				dic["label"] = field.label
				field_list.append(dic)

			return render_to_response('create_groupfield.html', {'field_list': field_list, },
					  context_instance=RequestContext(request))
		else:
			messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on creating groupfield!')
			return HttpResponseRedirect('/accounts/login')
	if request.method == 'POST': #save groupfield
		current_user = request.user
		is_active = current_user.is_active
		is_superuser = current_user.is_superuser
		if(is_active and is_superuser):
			groupfields = GroupField.objects.all()
			is_existed = False
			for groupfield in groupfields:
				if groupfield.name == request.POST['groupfield_name']:
					messages.add_message(request, messages.ERROR, 'ERROR: %s - GroupField already existed. Please select another name or edit the existing once!' % request.POST['groupfield_name'])
					is_existed = True
					break
			if is_existed:
				field_list = []
				selected_field_list = []

				selected_list = request.POST.getlist('selectto')
				for i in range(0, len(selected_list)):
					field_id = selected_list[i]
					field = Field.objects.get(id = field_id)
					dic = {}
					dic["id"] = field.id
					dic["label"] = field.label
					selected_field_list.append(dic)

				fields = Field.objects.all()
				for field in fields:
					is_selected = False
					for selected in selected_list:
						if str(selected) == str(field.id):
							is_selected = True
							break
					if is_selected == False:
						dic = {}
						dic["id"] = field.id
						dic["label"] = field.label
						field_list.append(dic)

				return render_to_response('create_groupfield.html', {'field_list': field_list, 'selected_field_list': selected_field_list,},
						  context_instance=RequestContext(request))
			else:
				#save field to groupfield
				groupfield = GroupField(name = request.POST['groupfield_name'])
				groupfield.save()
				selected_list = request.POST.getlist('selectto')
				for i in range(0, len(selected_list)):
					field_id = selected_list[i]
					field = Field.objects.get(id = field_id)
					groupfieldfield = GroupFieldField(index = i, field = field, groupfield = groupfield)
					groupfieldfield.save()
				messages.add_message(request, messages.SUCCESS, 'SUCCESS: You have success created GroupField: ' + groupfield.name)
				field_list = []
				fields = Field.objects.all()
				for field in fields:
					dic = {}
					dic["id"] = field.id
					dic["label"] = field.label
					field_list.append(dic)
				# return render_to_response('create_groupfield.html', {'field_list': field_list,},
				# 		  context_instance=RequestContext(request))
				return HttpResponseRedirect('/transaction/edit_groupfield?action=edit&groupfield_id=%s' % groupfield.id)
		else:
			messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on creating groupfield!')
			return HttpResponseRedirect('/accounts/login')

@csrf_exempt
def edit_groupfield(request):
	if request.method == 'GET' and request.GET['action'] == 'edit': #populate form for user to edit groupfield
		current_user = request.user
		is_active = current_user.is_active
		is_superuser = current_user.is_superuser
		if(is_active and is_superuser):
			groupfield = GroupField.objects.get(id = request.GET['groupfield_id'])
			groupfield_name = groupfield.name
			groupfield_id = groupfield.id

			field_list = []
			selected_field_list = []

			groupfieldfields = GroupFieldField.objects.filter(groupfield = groupfield)
			for groupfieldfield in groupfieldfields:
				field = groupfieldfield.field
				dic = {}
				dic["id"] = field.id
				dic["label"] = field.label
				selected_field_list.append(dic)

			fields = Field.objects.all()
			for field in fields:
				is_selected = False
				for groupfieldfield in groupfieldfields:
					if groupfieldfield.field.id == field.id:
						is_selected = True
						break
				if is_selected == False:
					dic = {}
					dic["id"] = field.id
					dic["label"] = field.label
					field_list.append(dic)

			return render_to_response('edit_groupfield.html', {'field_list': field_list,
															   'selected_field_list': selected_field_list,
															   'groupfield_name': groupfield_name,
															   'groupfield_id': groupfield_id,},
					  context_instance=RequestContext(request))
		else:
			messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on editing groupfield!')
			return HttpResponseRedirect('/accounts/login')
	if request.method == 'POST': #edit groupfield. Tell user if new name is existed, or groupfieldfield have value
		current_user = request.user
		is_active = current_user.is_active
		is_superuser = current_user.is_superuser
		if(is_active and is_superuser):
			#check name
			groupfield_edit = GroupField.objects.get(id = request.POST['groupfield_id'])
			groupfields = GroupField.objects.all()
			is_existed = False
			for groupfield in groupfields:
				if groupfield_edit.name != groupfield.name and groupfield.name == request.POST['groupfield_name']:
					messages.add_message(request, messages.ERROR, 'ERROR: %s - GroupField name already existed. Please select another name or edit the existing once!' % request.POST['groupfield_name'])
					is_existed = True
					break
			if is_existed:
				field_list = []
				selected_field_list = []

				groupfield_name = groupfield_edit.name
				groupfield_id = request.POST['groupfield_id']

				selected_list = request.POST.getlist('selectto')
				for i in range(0, len(selected_list)):
					field_id = selected_list[i]
					field = Field.objects.get(id = field_id)
					dic = {}
					dic["id"] = field.id
					dic["label"] = field.label
					selected_field_list.append(dic)

				fields = Field.objects.all()
				for field in fields:
					is_selected = False
					for selected in selected_list:
						if str(selected) == str(field.id):
							is_selected = True
							break
					if is_selected == False:
						dic = {}
						dic["id"] = field.id
						dic["label"] = field.label
						field_list.append(dic)

				return render_to_response('edit_groupfield.html', {'field_list': field_list,
																   'selected_field_list': selected_field_list,
																   'groupfield_name': groupfield_name,
																   'groupfield_id': groupfield_id,},
						  context_instance=RequestContext(request))
				#end check name
			else:
				#update groupfield name
				if groupfield_edit.name == request.POST['groupfield_name']:
					messages.add_message(request, messages.SUCCESS, 'SUCCESS: %s - GroupField name is the same as old name!' % request.POST['groupfield_name'])
				else:
					groupfield_edit.name = request.POST['groupfield_name']
					groupfield_edit.save()
					messages.add_message(request, messages.SUCCESS, 'SUCCESS: %s - GroupField name has been changed successfully!' % request.POST['groupfield_name'])

				#check if groupfield field change?
				groupfieldfields = GroupFieldField.objects.filter(groupfield = groupfield_edit).order_by('index')
				is_field_changed = False
				selected_list = request.POST.getlist('selectto')
				if len(groupfieldfields) != len(selected_list):
					is_field_changed = True
				else:
					for i in range(0, len(selected_list)):
						selected_id = selected_list[i]
						field_id = groupfieldfields[i].field.id
						if str(selected_id) != str(field_id):
							is_field_changed = True
							break
				if is_field_changed == True:
					#field changed, check uploadfilegroupfield
					fileuploadgroupfields = FileUploadGroupField.objects.filter(groupfield = groupfield_edit)
					if len(fileuploadgroupfields) > 0:
						messages.add_message(request, messages.ERROR, 'ERROR: %s - GroupField has been used in uploaded files. Could not change groupfield field!' % request.POST['groupfield_name'])
					else:
						#update groupfield fields
						groupfieldfields = GroupFieldField.objects.filter(groupfield = groupfield_edit)
						#delete old fields
						groupfieldfields.delete()
						#save new fields
						selected_list = request.POST.getlist('selectto')
						for i in range(0, len(selected_list)):
							field_id = selected_list[i]
							field = Field.objects.get(id = field_id)
							groupfieldfield = GroupFieldField(index = i, field = field, groupfield = groupfield_edit)
							groupfieldfield.save()
						messages.add_message(request, messages.SUCCESS, 'SUCCESS: %s - GroupField fields have been changed successfully!' % request.POST['groupfield_name'])
				else:
					messages.add_message(request, messages.SUCCESS, 'SUCCESS: %s - GroupField fields are the same as old fields!' % request.POST['groupfield_name'])
				#send response to user
				field_list = []
				selected_field_list = []

				groupfield_name = request.POST['groupfield_name']
				groupfield_id = request.POST['groupfield_id']

				selected_list = request.POST.getlist('selectto')
				for i in range(0, len(selected_list)):
					field_id = selected_list[i]
					field = Field.objects.get(id = field_id)
					dic = {}
					dic["id"] = field.id
					dic["label"] = field.label
					selected_field_list.append(dic)

				fields = Field.objects.all()
				for field in fields:
					is_selected = False
					for selected in selected_list:
						if str(selected) == str(field.id):
							is_selected = True
							break
					if is_selected == False:
						dic = {}
						dic["id"] = field.id
						dic["label"] = field.label
						field_list.append(dic)

				return render_to_response('edit_groupfield.html', {'field_list': field_list,
																   'selected_field_list': selected_field_list,
																   'groupfield_name': groupfield_name,
																   'groupfield_id': groupfield_id,},
						  context_instance=RequestContext(request))
		else:
			messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on editing groupfield!')
			return HttpResponseRedirect('/accounts/login')

@csrf_exempt
def delete_groupfield(request):
	#check if groupfield already have data, if yes the tell user cannot delete
	if request.method == 'GET' and request.GET['action'] == 'delete':
		current_user = request.user
		is_active = current_user.is_active
		is_superuser = current_user.is_superuser
		if(is_active and is_superuser):
			groupfield = GroupField.objects.get(id = request.GET['groupfield_id'])
			groupfield_name = groupfield.name
			formgroupfields = FormGroupField.objects.filter(groupfield = groupfield)
			if len(formgroupfields) > 0:
				#return message to user that cannot delete
				messages.add_message(request, messages.ERROR, 'ERROR: %s - Groupfield has been used in form. Could not delete!' % groupfield.name)
				groupfield_list = []
				groupfields = GroupField.objects.all()
				for groupfield in groupfields:
					dic = {}
					dic["id"] = groupfield.id
					dic["name"] = groupfield.name
					groupfield_list.append(dic)
				# return render_to_response('groupfield_list.html', {'groupfield_list': groupfield_list},
				# 		context_instance=RequestContext(request))
				return HttpResponseRedirect('/transaction/groupfield_list')
			else:
				#delete groupfieldfield and delete groupfield
				groupfieldfields = GroupFieldField.objects.filter(groupfield = groupfield)
				if len(groupfieldfields) > 0:
					groupfieldfields.delete()
				groupfield.delete()

				messages.add_message(request, messages.SUCCESS, 'SUCCESS: %s - Groupfield has been deleted!' % groupfield.name)
				return HttpResponseRedirect('/transaction/groupfield_list')
		else:
			messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on creating groupfield!')
			return HttpResponseRedirect() #tell user that don't have permission

@csrf_exempt
def create_form(request):
	#check if more than 1 groupfield then ask user to remove
	if request.method == 'GET': #populate form for user to create form
			current_user = request.user
			is_active = current_user.is_active
			is_superuser = current_user.is_superuser
			if(is_active and is_superuser):
				#get parameters from copy function
				groupforms = [] #OK
				companies = []  #OK
				forms = []      #OK
				fields = []     #OK
				groupfields = [] #OK
				formname = ''    #OK
				selectto = []    #OK

				all_fields = Field.objects.all()
				for all_field in all_fields:
					dic = {}
					dic["index"] = "Not available"
					dic["id"] = all_field.id
					dic["label"] = all_field.label
					fields.append(dic)

				all_groupfields = GroupField.objects.all()
				for all_groupfield in all_groupfields:
					dic = {}
					dic["index"] = "Not available"
					dic["id"] = all_groupfield.id
					dic["name"] = all_groupfield.name
					groupfields.append(dic)

				all_groupforms = GroupForm.objects.all()
				for all_groupform in all_groupforms:
					dic = {}
					dic["id"] = all_groupform.id
					dic["name"] = all_groupform.name
					dic["selected"] = ""
					groupforms.append(dic)

				all_companies = Company.objects.all()
				for all_company in all_companies:
					dic = {}
					dic["id"] = all_company.id
					dic["short_name"] = all_company.short_name
					dic["selected"] = ""
					companies.append(dic)

				all_forms = Form.objects.all()
				for all_form in all_forms:
					dic = {}
					dic["id"] = all_form.id
					dic["name"] = all_form.name
					dic["selected"] = ""
					forms.append(dic)

				return render_to_response('create_form.html', {'groupforms': groupforms,
															   'companies': companies,
															   'forms': forms,
															   'fields': fields,
															   'groupfields': groupfields,
															   'formname': formname,
															   'selectto': selectto,},
						  context_instance=RequestContext(request))
			else:
				messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on creating form!')
				return HttpResponseRedirect('/accounts/login')
	if request.method == 'POST': #save form
			current_user = request.user
			is_active = current_user.is_active
			is_superuser = current_user.is_superuser
			if(is_active and is_superuser):
				#get parameters and check data in database, if form existed, tell user to edit, else create

				forms = []
				fields = []
				companies = []
				groupforms = []
				groupfields = []
				formname = ''
				selectto = []

				if 'formname' in request.POST and 'groupform' in request.POST and 'selectto' in request.POST and 'comp' in request.POST:
					all_forms = Form.objects.all()
					is_existed = False
					groupfield_count = 0 #Multiple groupfield detected. You are allow to add 1 groupfield in a form

					for all_form in all_forms:
						if str(all_form.name) == str(request.POST['formname']):
							is_existed = True
							break
					if is_existed: #tell user to rename the form (response back to create_form)
						messages.add_message(request, messages.ERROR, 'ERROR: %s - Form name already existed. Please select another name or edit the existing once!' % request.POST['formname'])
						selected_list = request.POST.getlist('selectto')
						for i in range(0, len(selected_list)):
							field_id = selected_list[i]
							if "group_" in str(field_id):
								substrings = field_id.split('_')
								groupfield = GroupField.objects.get(id = substrings[1])
								dic = {}
								dic["id"] = "group_" + str(groupfield.id)
								dic["label"] = groupfield.name
								selectto.append(dic)
								groupfield_count = groupfield_count + 1
							else:
								field = Field.objects.get(id = field_id)
								dic = {}
								dic["id"] = field.id
								dic["label"] = field.label
								selectto.append(dic)

						if groupfield_count > 1:
							messages.add_message(request, messages.ERROR, 'ERROR: Multiple groupfield detected. You are allow to add 1 groupfield in a form')
						#end put selected field & groupfield to list
						formname = str(request.POST['formname'])

						all_groupfields = GroupField.objects.all()
						for all_groupfield in all_groupfields:
							is_used = False
							for dic in selectto:
								if "group_" + str(all_groupfield.id) == dic.get('id'):
									is_used = True
									break
							if is_used != True:
								dic = {}
								dic["index"] = "Not available"
								dic["id"] = all_groupfield.id
								dic["name"] = all_groupfield.name
								groupfields.append(dic)

						all_groupforms = GroupForm.objects.all()
						for all_groupform in all_groupforms:
							if str(all_groupform.id) == str(request.POST['groupform']):
								dic = {}
								dic["id"] = all_groupform.id
								dic["name"] = all_groupform.name
								dic["selected"] = "selected"
								groupforms.append(dic)
							else:
								dic = {}
								dic["id"] = all_groupform.id
								dic["name"] = all_groupform.name
								dic["selected"] = ""
								groupforms.append(dic)

						all_companies = Company.objects.all()
						for all_company in all_companies:
							if str(all_company.id) == str(request.POST['comp']):
								dic = {}
								dic["id"] = all_company.id
								dic["short_name"] = all_company.short_name
								dic["selected"] = "selected"
								companies.append(dic)
							else:
								dic = {}
								dic["id"] = all_company.id
								dic["short_name"] = all_company.short_name
								dic["selected"] = ""
								companies.append(dic)

						all_fields = Field.objects.all()
						for all_field in all_fields:
							is_selected = False
							for dic in selectto:
								if str(dic.get('id')) == str(all_field.id):
									is_selected = True
									break
							if is_selected == False:
								dic = {}
								dic["id"] = all_field.id
								dic["label"] = all_field.label
								fields.append(dic)

						all_forms = Form.objects.all()
						for all_form in all_forms:
							if str(all_form.id) == str(request.POST['fromform']):
								dic = {}
								dic["id"] = all_form.id
								dic["name"] = all_form.name
								dic["selected"] = "selected"
								forms.append(dic)
							else:
								dic = {}
								dic["id"] = all_form.id
								dic["name"] = all_form.name
								dic["selected"] = ""
								forms.append(dic)

						return render_to_response('create_form.html', {'groupforms': groupforms,
																	   'companies': companies,
																	   'forms': forms,
																	   'fields': fields,
																	   'groupfields': groupfields,
																	   'formname': formname,
																	   'selectto': selectto,},
								  context_instance=RequestContext(request))
					else:
						#check groupfield count
						selected_list = request.POST.getlist('selectto')
						for i in range(0, len(selected_list)):
							field_id = selected_list[i]
							if "group_" in str(field_id):
								groupfield_count = groupfield_count + 1
						if groupfield_count > 1:
							messages.add_message(request, messages.ERROR, 'ERROR: Multiple groupfield detected. You are allow to add 1 groupfield in a form')

							for i in range(0, len(selected_list)):
								field_id = selected_list[i]
								if "group_" in str(field_id):
									substrings = field_id.split('_')
									groupfield = GroupField.objects.get(id = substrings[1])
									dic = {}
									dic["id"] = "group_" + str(groupfield.id)
									dic["label"] = groupfield.name
									selectto.append(dic)
								else:
									field = Field.objects.get(id = field_id)
									dic = {}
									dic["id"] = field.id
									dic["label"] = field.label
									selectto.append(dic)

							#end put selected field & groupfield to list
							formname = str(request.POST['formname'])

							all_groupfields = GroupField.objects.all()
							for all_groupfield in all_groupfields:
								is_used = False
								for dic in selectto:
									if "group_" + str(all_groupfield.id) == dic.get('id'):
										is_used = True
										break
								if is_used != True:
									dic = {}
									dic["index"] = "Not available"
									dic["id"] = all_groupfield.id
									dic["name"] = all_groupfield.name
									groupfields.append(dic)

							all_groupforms = GroupForm.objects.all()
							for all_groupform in all_groupforms:
								if str(all_groupform.id) == str(request.POST['groupform']):
									dic = {}
									dic["id"] = all_groupform.id
									dic["name"] = all_groupform.name
									dic["selected"] = "selected"
									groupforms.append(dic)
								else:
									dic = {}
									dic["id"] = all_groupform.id
									dic["name"] = all_groupform.name
									dic["selected"] = ""
									groupforms.append(dic)

							all_companies = Company.objects.all()
							for all_company in all_companies:
								if str(all_company.id) == str(request.POST['comp']):
									dic = {}
									dic["id"] = all_company.id
									dic["short_name"] = all_company.short_name
									dic["selected"] = "selected"
									companies.append(dic)
								else:
									dic = {}
									dic["id"] = all_company.id
									dic["short_name"] = all_company.short_name
									dic["selected"] = ""
									companies.append(dic)

							all_fields = Field.objects.all()
							for all_field in all_fields:
								is_selected = False
								for dic in selectto:
									if str(dic.get('id')) == str(all_field.id):
										is_selected = True
										break
								if is_selected == False:
									dic = {}
									dic["id"] = all_field.id
									dic["label"] = all_field.label
									fields.append(dic)

							all_forms = Form.objects.all()
							for all_form in all_forms:
								if str(all_form.id) == str(request.POST['fromform']):
									dic = {}
									dic["id"] = all_form.id
									dic["name"] = all_form.name
									dic["selected"] = "selected"
									forms.append(dic)
								else:
									dic = {}
									dic["id"] = all_form.id
									dic["name"] = all_form.name
									dic["selected"] = ""
									forms.append(dic)

							return render_to_response('create_form.html', {'groupforms': groupforms,
																		   'companies': companies,
																		   'forms': forms,
																		   'fields': fields,
																		   'groupfields': groupfields,
																		   'formname': formname,
																		   'selectto': selectto,},
									  context_instance=RequestContext(request))
						else:
							#save form to db
							company = Company.objects.get(id = str(request.POST['comp']))
							groupform = GroupForm.objects.get(id = str(request.POST['groupform']))
							form = Form(name = str(request.POST['formname']), company = company, groupform = groupform)
							form.save()
							selected_list = request.POST.getlist('selectto')
							for i in range(0, len(selected_list)):
								field_id = selected_list[i]
								if "group_" in str(field_id):
									substrings = field_id.split('_')
									groupfield = GroupField.objects.get(id = substrings[1])
									formgroupfield = FormGroupField(index = i, form = form, groupfield = groupfield)
									formgroupfield.save()
								else:
									field = Field.objects.get(id = field_id)
									formfield = FormField(index = i, field = field, form = form)
									formfield.save()
							#end saving
							messages.add_message(request, messages.SUCCESS, 'SUCCESS: %s - Form has been created successfully!' % request.POST['formname'])
							return HttpResponseRedirect('/transaction/edit_form?action=edit&form_id=%s'%form.id)
				##########################
				elif 'form_id' in request.POST and 'form_name' in request.POST and 'group_form' in request.POST and 'company' in request.POST:

					form_id = request.POST['form_id']

					form_name = request.POST['form_name']
					formname = form_name
					groupform_id = request.POST['group_form']
					company_id = request.POST['company']

					form = Form.objects.get(id = form_id)
					formgroupfields = FormGroupField.objects.filter(form = form)
					formfields = FormField.objects.filter(form = form)

					all_fields = Field.objects.all()
					selectto_list = []
					for all_field in all_fields:
						is_used = False
						formfield_index = ''
						for formfield in formfields:
							if formfield.field.id == all_field.id:
								is_used = True
								formfield_index = formfield.index
								break
						if is_used == True:
							dic = {}
							dic["index"] = formfield_index
							dic["id"] = all_field.id
							dic["label"] = all_field.label
							selectto_list.append(dic)
						else:
							dic = {}
							dic["index"] = "Not available"
							dic["id"] = all_field.id
							dic["label"] = all_field.label
							fields.append(dic)

					all_groupfields = GroupField.objects.all()
					for all_groupfield in all_groupfields:
						is_used = False
						formgroupfield_index = ''
						for formgroupfield in formgroupfields:
							if all_groupfield.id == formgroupfield.groupfield.id:
								formgroupfield_index = formgroupfield.index
								is_used = True
								break
						if is_used == True:
							dic = {}
							dic["index"] = formgroupfield_index
							dic["id"] = 'group_' + str(all_groupfield.id)
							dic["label"] = all_groupfield.name
							selectto_list.append(dic)
						else:
							dic = {}
							dic["index"] = "Not available"
							dic["id"] = all_groupfield.id
							dic["name"] = all_groupfield.name
							groupfields.append(dic)

					all_groupforms = GroupForm.objects.all()
					for all_groupform in all_groupforms:
						if str(all_groupform.id) == str(groupform_id):
							dic = {}
							dic["id"] = all_groupform.id
							dic["name"] = all_groupform.name
							dic["selected"] = "selected"
							groupforms.append(dic)
						else:
							dic = {}
							dic["id"] = all_groupform.id
							dic["name"] = all_groupform.name
							dic["selected"] = ""
							groupforms.append(dic)

					all_companies = Company.objects.all()
					for all_company in all_companies:
						if str(all_company.id) == str(company_id):
							dic = {}
							dic["id"] = all_company.id
							dic["short_name"] = all_company.short_name
							dic["selected"] = "selected"
							companies.append(dic)
						else:
							dic = {}
							dic["id"] = all_company.id
							dic["short_name"] = all_company.short_name
							dic["selected"] = ""
							companies.append(dic)

					all_forms = Form.objects.all()
					for all_form in all_forms:
						if str(all_form.id) == str(form_id):
							dic = {}
							dic["id"] = all_form.id
							dic["name"] = all_form.name
							dic["selected"] = "selected"
							forms.append(dic)
						else:
							dic = {}
							dic["id"] = all_form.id
							dic["name"] = all_form.name
							dic["selected"] = ""
							forms.append(dic)

					selectto = sorted(selectto_list, key=itemgetter('index'))

					return render_to_response('create_form.html', {'groupforms': groupforms,
																   'companies': companies,
																   'forms': forms,
																   'fields': fields,
																   'groupfields': groupfields,
																   'formname': formname,
																   'selectto': selectto ,},
											  context_instance=RequestContext(request))
				####################
				else:
					#post parameter does not exist
					messages.add_message(request, messages.ERROR, 'ERROR: Could not find valid parameters to create form. Please create again!')
					all_fields = Field.objects.all()
					for all_field in all_fields:
						dic = {}
						dic["index"] = "Not available"
						dic["id"] = all_field.id
						dic["label"] = all_field.label
						fields.append(dic)

					all_groupfields = GroupField.objects.all()
					for all_groupfield in all_groupfields:
						dic = {}
						dic["index"] = "Not available"
						dic["id"] = all_groupfield.id
						dic["name"] = all_groupfield.name
						groupfields.append(dic)

					all_groupforms = GroupForm.objects.all()
					for all_groupform in all_groupforms:
						dic = {}
						dic["id"] = all_groupform.id
						dic["name"] = all_groupform.name
						dic["selected"] = ""
						groupforms.append(dic)

					all_companies = Company.objects.all()
					for all_company in all_companies:
						dic = {}
						dic["id"] = all_company.id
						dic["short_name"] = all_company.short_name
						dic["selected"] = ""
						companies.append(dic)

					all_forms = Form.objects.all()
					for all_form in all_forms:
						dic = {}
						dic["id"] = all_form.id
						dic["name"] = all_form.name
						dic["selected"] = ""
						forms.append(dic)

					return render_to_response('create_form.html', {'groupforms': groupforms,
																   'companies': companies,
																   'forms': forms,
																   'fields': fields,
																   'groupfields': groupfields,
																   'formname': formname,
																   'selectto': selectto,},
							  context_instance=RequestContext(request))
			else:
				#tell user does not have permission
				messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on creating form!')
				return HttpResponseRedirect('/accounts/login')
	#done for create form

@csrf_exempt
def edit_form(request):
	if request.method == 'GET': #populate form for user to edit form
			current_user = request.user
			is_active = current_user.is_active
			is_superuser = current_user.is_superuser
			if(is_active and is_superuser):
				#get parameters from copy function
				groupforms = [] #OK
				companies = []  #OK
				forms = []      #dont need to set selected
				fields = []     #OK
				groupfields = [] #OK
				formname = ''    #OK
				selectto = []    #OK
				edit_form_id = ''

				if 'form_id' in request.GET and 'action' in request.GET:
					edit_form_id = request.GET['form_id']
					form = Form.objects.get(id = request.GET['form_id'])
					formname = form.name
					formgroupfields = FormGroupField.objects.filter(form = form)
					formfields = FormField.objects.filter(form = form)

					all_fields = Field.objects.all()
					selectto_list = []
					for all_field in all_fields:
						is_used = False
						formfield_index = ''
						for formfield in formfields:
							if formfield.field.id == all_field.id:
								is_used = True
								formfield_index = formfield.index
								break
						if is_used == True:
							dic = {}
							dic["index"] = formfield_index
							dic["id"] = all_field.id
							dic["label"] = all_field.label
							selectto_list.append(dic)
						else:
							dic = {}
							dic["index"] = "Not available"
							dic["id"] = all_field.id
							dic["label"] = all_field.label
							fields.append(dic)

					all_groupfields = GroupField.objects.all()
					for all_groupfield in all_groupfields:
						is_used = False
						formgroupfield_index = ''
						for formgroupfield in formgroupfields:
							if all_groupfield.id == formgroupfield.groupfield.id:
								formgroupfield_index = formgroupfield.index
								is_used = True
								break
						if is_used == True:
							dic = {}
							dic["index"] = formgroupfield_index
							dic["id"] = 'group_' + str(all_groupfield.id)
							dic["label"] = all_groupfield.name
							selectto_list.append(dic)
						else:
							dic = {}
							dic["index"] = "Not available"
							dic["id"] = all_groupfield.id
							dic["name"] = all_groupfield.name
							groupfields.append(dic)

					all_groupforms = GroupForm.objects.all()
					for all_groupform in all_groupforms:
						if all_groupform.id == form.groupform.id:
							dic = {}
							dic["id"] = all_groupform.id
							dic["name"] = all_groupform.name
							dic["selected"] = "selected"
							groupforms.append(dic)
						else:
							dic = {}
							dic["id"] = all_groupform.id
							dic["name"] = all_groupform.name
							dic["selected"] = ""
							groupforms.append(dic)

					all_companies = Company.objects.all()
					for all_company in all_companies:
						if all_company.id == form.company.id:
							dic = {}
							dic["id"] = all_company.id
							dic["short_name"] = all_company.short_name
							dic["selected"] = "selected"
							companies.append(dic)
						else:
							dic = {}
							dic["id"] = all_company.id
							dic["short_name"] = all_company.short_name
							dic["selected"] = ""
							companies.append(dic)

					all_forms = Form.objects.all()
					for all_form in all_forms:
						if all_form.id == form.id:
							dic = {}
							dic["id"] = all_form.id
							dic["name"] = all_form.name
							dic["selected"] = "selected"
							forms.append(dic)
						else:
							dic = {}
							dic["id"] = all_form.id
							dic["name"] = all_form.name
							dic["selected"] = ""
							forms.append(dic)

					selectto = sorted(selectto_list, key=itemgetter('index'))

					return render_to_response('edit_form.html', {'groupforms': groupforms,
																   'companies': companies,
																   'forms': forms,
																   'fields': fields,
																   'groupfields': groupfields,
																   'formname': formname,
																   'selectto': selectto,
																   'edit_form_id': edit_form_id,},
							  context_instance=RequestContext(request))
				# just return the list
				else: #tell user cannot find valid parameter for the action, and return to form_list
					messages.add_message(request, messages.ERROR, 'ERROR: Could not find valid parameters to get a form. Please select a form again!')
					return HttpResponseRedirect('/transaction/form_list')
			else:
				messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on editing form!')
				return HttpResponseRedirect('/accounts/login')
	if request.method == 'POST': #save form
			current_user = request.user
			is_active = current_user.is_active
			is_superuser = current_user.is_superuser
			if(is_active and is_superuser):
				#get parameters and check data in database, if form existed, tell user to edit, else create

				forms = []
				fields = []
				companies = []
				groupforms = []
				groupfields = []
				formname = ''
				selectto = []
				edit_form_id = ''

				if 'edit_form_id' in request.POST and 'formname' in request.POST and 'groupform' in request.POST and 'selectto' in request.POST and 'comp' in request.POST:
					#check if the form have been used in any upload file
					form = Form.objects.get(id = request.POST['edit_form_id'])
					form_name = form.name
					fileuploads = FileUpload.objects.filter(form = form)
					if len(fileuploads) > 0:
						#return message to user that cannot edit
						messages.add_message(request, messages.ERROR, 'ERROR: %s - Form has been used in uploaded files. Could not edit!' % form_name)
						return HttpResponseRedirect('/transaction/form_list')
					#end checking
					else: #form have not been used by any uploaded files, can edit
						all_forms = Form.objects.all()
						is_existed = False
						groupfield_count = 0 #Multiple groupfield detected. You are allow to add 1 groupfield in a form

						for all_form in all_forms:
							if str(all_form.name) == str(request.POST['formname']) and all_form.name != form.name:
								is_existed = True
								break
						if is_existed: #tell user to rename the form (response back to create_form)
							messages.add_message(request, messages.ERROR, 'ERROR: %s - Form name already existed. Please select another name or edit the existing once!' % request.POST['formname'])
							selected_list = request.POST.getlist('selectto')
							for i in range(0, len(selected_list)):
								field_id = selected_list[i]
								if "group_" in str(field_id):
									substrings = field_id.split('_')
									groupfield = GroupField.objects.get(id = substrings[1])
									dic = {}
									dic["id"] = "group_" + str(groupfield.id)
									dic["label"] = groupfield.name
									selectto.append(dic)
									groupfield_count = groupfield_count + 1
								else:
									field = Field.objects.get(id = field_id)
									dic = {}
									dic["id"] = field.id
									dic["label"] = field.label
									selectto.append(dic)

							if groupfield_count > 1:
								messages.add_message(request, messages.ERROR, 'ERROR: Multiple groupfield detected. You are allow to add 1 groupfield in a form')
							#end put selected field & groupfield to list
							formname = str(request.POST['formname'])

							all_groupfields = GroupField.objects.all()
							for all_groupfield in all_groupfields:
								is_used = False
								for dic in selectto:
									if "group_" + str(all_groupfield.id) == dic.get('id'):
										is_used = True
										break
								if is_used != True:
									dic = {}
									dic["index"] = "Not available"
									dic["id"] = all_groupfield.id
									dic["name"] = all_groupfield.name
									groupfields.append(dic)

							all_groupforms = GroupForm.objects.all()
							for all_groupform in all_groupforms:
								if str(all_groupform.id) == str(request.POST['groupform']):
									dic = {}
									dic["id"] = all_groupform.id
									dic["name"] = all_groupform.name
									dic["selected"] = "selected"
									groupforms.append(dic)
								else:
									dic = {}
									dic["id"] = all_groupform.id
									dic["name"] = all_groupform.name
									dic["selected"] = ""
									groupforms.append(dic)

							all_companies = Company.objects.all()
							for all_company in all_companies:
								if str(all_company.id) == str(request.POST['comp']):
									dic = {}
									dic["id"] = all_company.id
									dic["short_name"] = all_company.short_name
									dic["selected"] = "selected"
									companies.append(dic)
								else:
									dic = {}
									dic["id"] = all_company.id
									dic["short_name"] = all_company.short_name
									dic["selected"] = ""
									companies.append(dic)

							all_fields = Field.objects.all()
							for all_field in all_fields:
								is_selected = False
								for dic in selectto:
									if str(dic.get('id')) == str(all_field.id):
										is_selected = True
										break
								if is_selected == False:
									dic = {}
									dic["id"] = all_field.id
									dic["label"] = all_field.label
									fields.append(dic)

							all_forms = Form.objects.all()
							for all_form in all_forms:
								if str(all_form.id) == str(request.POST['fromform']):
									dic = {}
									dic["id"] = all_form.id
									dic["name"] = all_form.name
									dic["selected"] = "selected"
									forms.append(dic)
								else:
									dic = {}
									dic["id"] = all_form.id
									dic["name"] = all_form.name
									dic["selected"] = ""
									forms.append(dic)

							return render_to_response('edit_form.html', {'groupforms': groupforms,
																		   'companies': companies,
																		   'forms': forms,
																		   'fields': fields,
																		   'groupfields': groupfields,
																		   'formname': formname,
																		   'selectto': selectto,
																		   'edit_form_id': edit_form_id,},
									  context_instance=RequestContext(request))
						else:
							#check groupfield count
							selected_list = request.POST.getlist('selectto')
							for i in range(0, len(selected_list)):
								field_id = selected_list[i]
								if "group_" in str(field_id):
									groupfield_count = groupfield_count + 1
							if groupfield_count > 1:
								messages.add_message(request, messages.ERROR, 'ERROR: Multiple groupfield detected. You are allow to add 1 groupfield in a form')

								for i in range(0, len(selected_list)):
									field_id = selected_list[i]
									if "group_" in str(field_id):
										substrings = field_id.split('_')
										groupfield = GroupField.objects.get(id = substrings[1])
										dic = {}
										dic["id"] = "group_" + str(groupfield.id)
										dic["label"] = groupfield.name
										selectto.append(dic)
									else:
										field = Field.objects.get(id = field_id)
										dic = {}
										dic["id"] = field.id
										dic["label"] = field.label
										selectto.append(dic)

								#end put selected field & groupfield to list
								formname = str(request.POST['formname'])

								all_groupfields = GroupField.objects.all()
								for all_groupfield in all_groupfields:
									is_used = False
									for dic in selectto:
										if "group_" + str(all_groupfield.id) == dic.get('id'):
											is_used = True
											break
									if is_used != True:
										dic = {}
										dic["index"] = "Not available"
										dic["id"] = all_groupfield.id
										dic["name"] = all_groupfield.name
										groupfields.append(dic)

								all_groupforms = GroupForm.objects.all()
								for all_groupform in all_groupforms:
									if str(all_groupform.id) == str(request.POST['groupform']):
										dic = {}
										dic["id"] = all_groupform.id
										dic["name"] = all_groupform.name
										dic["selected"] = "selected"
										groupforms.append(dic)
									else:
										dic = {}
										dic["id"] = all_groupform.id
										dic["name"] = all_groupform.name
										dic["selected"] = ""
										groupforms.append(dic)

								all_companies = Company.objects.all()
								for all_company in all_companies:
									if str(all_company.id) == str(request.POST['comp']):
										dic = {}
										dic["id"] = all_company.id
										dic["short_name"] = all_company.short_name
										dic["selected"] = "selected"
										companies.append(dic)
									else:
										dic = {}
										dic["id"] = all_company.id
										dic["short_name"] = all_company.short_name
										dic["selected"] = "selected"
										companies.append(dic)

								all_fields = Field.objects.all()
								for all_field in all_fields:
									is_selected = False
									for dic in selectto:
										if str(dic.get('id')) == str(all_field.id):
											is_selected = True
											break
									if is_selected == False:
										dic = {}
										dic["id"] = all_field.id
										dic["label"] = all_field.label
										fields.append(dic)

								all_forms = Form.objects.all()
								for all_form in all_forms:
									if str(all_form.id) == str(request.POST['fromform']):
										dic = {}
										dic["id"] = all_form.id
										dic["name"] = all_form.name
										dic["selected"] = "selected"
										forms.append(dic)
									else:
										dic = {}
										dic["id"] = all_form.id
										dic["name"] = all_form.name
										dic["selected"] = ""
										forms.append(dic)

								return render_to_response('edit_form.html', {'groupforms': groupforms,
																			   'companies': companies,
																			   'forms': forms,
																			   'fields': fields,
																			   'groupfields': groupfields,
																			   'formname': formname,
																			   'selectto': selectto,
																			   'edit_form_id': edit_form_id},
										  context_instance=RequestContext(request))
							else:
								#delete formfield and formgroupfield before saving the form
								#save form to db
								formgroupfield = FormGroupField.objects.filter(form = form)
								if len(formgroupfield) > 0:
									formgroupfield.delete()

								formfield = FormField.objects.filter(form = form)
								if len(formfield) > 0:
									formfield.delete()

								company = Company.objects.get(id = str(request.POST['comp']))
								groupform = GroupForm.objects.get(id = str(request.POST['groupform']))

								form.company = company
								form.groupform = groupform
								form.name = str(request.POST['formname'])
								form.save()

								selected_list = request.POST.getlist('selectto')
								for i in range(0, len(selected_list)):
									field_id = selected_list[i]
									if "group_" in str(field_id):
										substrings = field_id.split('_')
										groupfield = GroupField.objects.get(id = substrings[1])
										formgroupfield = FormGroupField(index = i, form = form, groupfield = groupfield)
										formgroupfield.save()
									else:
										field = Field.objects.get(id = field_id)
										formfield = FormField(index = i, field = field, form = form)
										formfield.save()
								#end saving

								messages.add_message(request, messages.SUCCESS, 'SUCCESS: %s - Form has been edited successfully!' % request.POST['formname'])
								return HttpResponseRedirect('/transaction/edit_form?action=edit&form_id=%s'%form.id)

					#end if/else checking upload file
				##########################
				elif 'edit_form_id' in request.POST and 'form_id' in request.POST and 'form_name' in request.POST and 'group_form' in request.POST and 'company' in request.POST:

					form_id = request.POST['form_id']
					edit_form_id = request.POST['edit_form_id']
					form_name = request.POST['form_name']
					formname = form_name
					groupform_id = request.POST['group_form']
					company_id = request.POST['company']

					form = Form.objects.get(id = form_id)
					formgroupfields = FormGroupField.objects.filter(form = form)
					formfields = FormField.objects.filter(form = form)

					all_fields = Field.objects.all()
					selectto_list = []
					for all_field in all_fields:
						is_used = False
						formfield_index = ''
						for formfield in formfields:
							if formfield.field.id == all_field.id:
								is_used = True
								formfield_index = formfield.index
								break
						if is_used == True:
							dic = {}
							dic["index"] = formfield_index
							dic["id"] = all_field.id
							dic["label"] = all_field.label
							selectto_list.append(dic)
						else:
							dic = {}
							dic["index"] = "Not available"
							dic["id"] = all_field.id
							dic["label"] = all_field.label
							fields.append(dic)

					all_groupfields = GroupField.objects.all()
					for all_groupfield in all_groupfields:
						is_used = False
						formgroupfield_index = ''
						for formgroupfield in formgroupfields:
							if all_groupfield.id == formgroupfield.groupfield.id:
								formgroupfield_index = formgroupfield.index
								is_used = True
								break
						if is_used == True:
							dic = {}
							dic["index"] = formgroupfield_index
							dic["id"] = 'group_' + str(all_groupfield.id)
							dic["label"] = all_groupfield.name
							selectto_list.append(dic)
						else:
							dic = {}
							dic["index"] = "Not available"
							dic["id"] = all_groupfield.id
							dic["name"] = all_groupfield.name
							groupfields.append(dic)

					all_groupforms = GroupForm.objects.all()
					for all_groupform in all_groupforms:
						if str(all_groupform.id) == str(groupform_id):
							dic = {}
							dic["id"] = all_groupform.id
							dic["name"] = all_groupform.name
							dic["selected"] = "selected"
							groupforms.append(dic)
						else:
							dic = {}
							dic["id"] = all_groupform.id
							dic["name"] = all_groupform.name
							dic["selected"] = ""
							groupforms.append(dic)

					all_companies = Company.objects.all()
					for all_company in all_companies:
						if str(all_company.id) == str(company_id):
							dic = {}
							dic["id"] = all_company.id
							dic["short_name"] = all_company.short_name
							dic["selected"] = "selected"
							companies.append(dic)
						else:
							dic = {}
							dic["id"] = all_company.id
							dic["short_name"] = all_company.short_name
							dic["selected"] = ""
							companies.append(dic)

					all_forms = Form.objects.all()
					for all_form in all_forms:
						if str(all_form.id) == str(form_id):
							dic = {}
							dic["id"] = all_form.id
							dic["name"] = all_form.name
							dic["selected"] = "selected"
							forms.append(dic)
						else:
							dic = {}
							dic["id"] = all_form.id
							dic["name"] = all_form.name
							dic["selected"] = ""
							forms.append(dic)

					selectto = sorted(selectto_list, key=itemgetter('index'))

					return render_to_response('edit_form.html', {'groupforms': groupforms,
																   'companies': companies,
																   'forms': forms,
																   'fields': fields,
																   'groupfields': groupfields,
																   'formname': formname,
																   'selectto': selectto,
																   'edit_form_id': edit_form_id, },
											  context_instance=RequestContext(request))
				####################
				else:
					#post parameter does not exist
					messages.add_message(request, messages.ERROR, 'ERROR: Could not find valid parameters to save the form. Please select a form again!')
					return HttpResponseRedirect('/transaction/form_list')
			else:
				#tell user does not have permission
				messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on editing form!')
				return HttpResponseRedirect('/accounts/login')
	#done for create form
	return ""

@csrf_exempt
def delete_form(request):
	#check if form already have data, if yes the tell user cannot delete
	if request.method == 'GET' and request.GET['action'] == 'delete':
		current_user = request.user
		is_active = current_user.is_active
		is_superuser = current_user.is_superuser
		if(is_active and is_superuser):
			form = Form.objects.get(id = request.GET['form_id'])
			form_name = form.name
			fileuploads = FileUpload.objects.filter(form = form)
			if len(fileuploads) > 0:
				#return message to user that cannot delete
				messages.add_message(request, messages.ERROR, 'ERROR: %s - Form has been used in uploaded files. Could not delete!' % form_name)
				return HttpResponseRedirect('/transaction/form_list')
			else:
				#delete formfield, formgroupfield, and form

				formgroupfield = FormGroupField.objects.filter(form = form)
				if len(formgroupfield) > 0:
					formgroupfield.delete()

				formfield = FormField.objects.filter(form = form)
				if len(formfield) > 0:
					formfield.delete()

				form.delete()

				messages.add_message(request, messages.SUCCESS, 'SUCCESS: %s - Form has been deleted!' % form_name)

				return HttpResponseRedirect('/transaction/form_list')
		else:
			messages.add_message(request, messages.ERROR, 'ERROR: You do not have permission on viewing form list!')
			return HttpResponseRedirect('/accounts/login')



