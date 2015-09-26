# encoding: utf-8
import json
import datetime
from django.http import HttpResponse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from .response import JSONResponse, response_mimetype
from .serialize import serialize
from .models import FileUpload, FileTiff
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
import os
from django.conf import settings
from decimal import *
from tools import filesizeformat
from transaction.models import GroupForm, Form
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from userprofile.decorators import permission_access_page_required


class FileCreateView(CreateView):
	model = FileUpload
	fields = "__all__"

	def form_valid(self, form):
		form.cleaned_data["user_upload"] = self.request.user
		form.cleaned_data["note"] = self.request.POST["note"]
		form.cleaned_data["form"] = Form.objects.get(id=self.request.POST["form"])

		form.instance.user_upload = self.request.user
		form.instance.user_upload_id = self.request.user.id
		form.instance.form = Form.objects.get(id=self.request.POST["form"])
		form.instance.form_id = self.request.POST["form"]

		self.object = form.save()

		form.instance.convert_to_jpg(612, 792)

		files = [serialize(self.object)]
		data = {'files': files}
		response = JSONResponse(data, mimetype=response_mimetype(self.request))
		response['Content-Disposition'] = 'inline; filename=files.json'
		
		#form.convert_to_png(612, 792)
		return response

	def form_invalid(self, form):
		data = json.dumps(form.errors)
		return HttpResponse(content=data, status=400, content_type='application/json')


class FileDeleteView(DeleteView):
	model = FileUpload

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.delete()
		response = JSONResponse(True, mimetype=response_mimetype(request))
		response['Content-Disposition'] = 'inline; filename=files.json'
		return response


class FileEditView(UpdateView):
	model = FileUpload
	template_name = "uploading/edit_upload.html"
	fields = ["form", "name", "note"]
	success_url = ""
	messages = {
		"file_update": {
			"level": messages.SUCCESS,
			"text": _("Note file is updated")
		},
	}

	def get_context_data(self, **kwargs):
		context = super(FileEditView, self).get_context_data(**kwargs)
		object_upload_file = context["object"]
		context['file_id'] = self.kwargs.get("pk", None)
		context['form_name'] = object_upload_file.form.name
		context['group_form'] = object_upload_file.form.groupform.name
		context['upload_date'] = object_upload_file.upload_date
		return context

	# def get(self, request, *args, **kwargs):
	# 	if "action" in self.request.GET:
	# 		group_form = self.get_group_forms()
	# 		return HttpResponse(json.dumps(group_form), content_type="application/json")
	# 	else:
	# 		return super(FileEditView, self).get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form):
		file = FileUpload.objects.get(id=self.kwargs.get("pk", None))
		file.note = self.request.POST["note"]
		if "form" in self.request.POST:
			file.form = Form.objects.get(id=self.request.POST["form"])
		file.save()
		self.success_url = "/upload/edit/" + str(self.kwargs.get("pk", None))
		messages.add_message(
			self.request,
			self.messages["file_update"]["level"],
			"SUCCESS: %s - Note file has been updated successfully!" % (file.name)
		)
		return super(FileEditView, self).form_valid(form)

	def form_invalid(self, form):
		data = json.dumps(form.errors)
		return HttpResponse(content=data, status=400, content_type='application/json')

	def get_group_forms(self):
		user = self.request.user
		group_forms_json = []
		if user.user_profile.is_customer_superadmin:
			company_id = user.user_profile.company.id
			form = Form.objects.filter(company__id=company_id)

			group_form_object_check = {}
			items_selected = 0
			for f in form:
				try:
					index = group_form_object_check[str(f.groupform.id)]
					group_forms_json[index]["forms"].append({
						"id": f.id,
						"name": f.name
					})
				except KeyError:
					group_form_object = {}
					group_form = f.groupform
					group_form_object["id"] = group_form.id
					group_form_object["name"] = group_form.name
					group_form_object["forms"] = []
					group_form_object["forms"].append({
						"id": f.id,
						"name": f.name
					})
					group_forms_json.append(group_form_object)
					group_form_object_check[str(f.groupform.id)] = items_selected
					items_selected += 1
		else:
			company_id = user.user_profile.company.id
			_form = Form.objects.filter(company__id=company_id)

			if _form:
				forms_permission = User.objects.get(
					id=self.request.user.id
				).user_profile.permission.all()

				if forms_permission:
					user_permission_array = []
					for form_permission in forms_permission:
						user_permission_array.append(int(form_permission.id))

					form = Form.objects.filter(id__in=user_permission_array)

					group_form_object_check = {}
					items_selected = 0
					for f in form:
						try:
							index = group_form_object_check[str(f.groupform.id)]
							group_forms_json[index]["forms"].append({
								"id": f.id,
								"name": f.name
							})
						except KeyError:
							group_form_object = {}
							group_form = f.groupform
							group_form_object["id"] = group_form.id
							group_form_object["name"] = group_form.name
							group_form_object["forms"] = []
							group_form_object["forms"].append({
								"id": f.id,
								"name": f.name
							})
							group_forms_json.append(group_form_object)
							group_form_object_check[str(f.groupform.id)] = items_selected
							items_selected += 1
		return group_forms_json


class HistoryUploadFile(ListView):
	model = FileUpload
	paginate_by = 20
	template_name = "uploading/list_file_upload.html"

	def get_context_data(self, **kwargs):
		context = super(HistoryUploadFile, self).get_context_data(**kwargs)

		new_object_list = []
		for object in context["object_list"]:
			new_object = {}
			new_object["id"] = object.id
			new_object["name"] = object.name
			new_object["file"] = object.file
			new_object["note"] = object.note.replace("\r\n", " ")
			new_object["form"] = object.form
			new_object["upload_date"] = object.upload_date.strftime("%b %d, %Y, %I:%M %p")
			new_object["process_date"] = None
			if object.process_date:
				new_object["process_date"] = object.process_date.strftime("%b %d, %Y, %I:%M %p")
			new_object["user_process"] = object.user_process

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
		return context

	def get_queryset(self):
		query_dict = {}
		if self.request.GET.get("q"):
			query_dict["name__icontains"] = self.request.GET.get("q")

		user = self.request.user
		queryset = FileUpload.objects.filter(
			user_upload=user,
			**query_dict
		).order_by("-id")

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
				new_object["real_size"] = object.file.size
				new_object["note"] = object.note.replace("\r\n", " ")
				new_object["form"] = object.form.name
				new_object["upload_date"] = object.upload_date.strftime("%b %d, %Y, %I:%M %p")
				# new_object["user_process"] = object.user_process

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
			return super(HistoryUploadFile, self).render_to_response(context, **kwargs)


class Dashboard(ListView):
	model = FileUpload
	paginate_by = 20
	template_name = "dashboard.html"

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated():
			if self.request.user.is_staff:
				if self.request.user.is_superuser:
					return HttpResponseRedirect("/user/list_all_user/")
				else:
					return HttpResponseRedirect("/user/profile/")
		else:
			return HttpResponseRedirect("/accounts/login")

		return super(Dashboard, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(Dashboard, self).get_context_data(**kwargs)

		new_object_list = []
		for object in context["object_list"]:
			new_object = {}
			new_object["id"] = object.id
			new_object["name"] = object.name
			new_object["file"] = object.file
			new_object["note"] = object.note.replace("\r\n", " ")
			new_object["form"] = object.form
			new_object["upload_date"] = object.upload_date.strftime("%b %d, %Y, %I:%M %p")
			new_object["process_date"] = object.process_date.strftime("%b %d, %Y, %I:%M %p")
			new_object["user_process"] = object.user_process

			file_tiff = FileTiff.objects.filter(fileupload=object)
			file_tiff_process = FileTiff.objects.filter(
				fileupload=object,
				status=1
			)

			new_object["file_process"] = "%s/%s Pages" % (len(file_tiff_process), len(file_tiff))
			new_object["progress"] = int(Decimal(len(file_tiff_process))/Decimal(len(file_tiff))*100)
			new_object["is_finish_process"] = True if len(file_tiff_process) == len(file_tiff) else False
			new_object["is_start_process"] = True if len(file_tiff_process) > 0 else False

			new_object_list.append(new_object)

		context["new_object_list"] = new_object_list
		return context

	def get_queryset(self):
		query_dict = {}
		if self.request.GET.get("q"):
			query_dict["name__icontains"] = self.request.GET.get("q")
		user = self.request.user
		queryset = FileUpload.objects.filter(user_upload=user, **query_dict).exclude(user_process=None).order_by("-process_date")
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
				new_object["real_size"] = object.file.size
				new_object["size"] = filesizeformat(object.file.size)
				new_object["note"] = object.note.replace("\r\n", " ")
				new_object["form"] = object.form.name
				new_object["upload_date"] = object.upload_date.strftime("%b %d, %Y, %I:%M %p")
				new_object["process_date"] = object.process_date.strftime("%b %d, %Y, %I:%M %p")
				new_object["user_process"] = object.user_process.last_name + " " + object.user_process.first_name

				file_tiff = FileTiff.objects.filter(fileupload=object)
				file_tiff_process = FileTiff.objects.filter(
					fileupload=object,
					status=1
				)
				new_object["file_process"] = "%s/%s Pages" % (len(file_tiff_process), len(file_tiff))
				new_object["progress"] = int(Decimal(len(file_tiff_process))/Decimal(len(file_tiff))*100)
				new_object["is_finish_process"] = True if len(file_tiff_process) == len(file_tiff) else False
				new_object["is_start_process"] = True if len(file_tiff_process) > 0 else False

				new_object_list.append(new_object)

			object_json["items"] = new_object_list
			object_json["has_next"] = False
			object_json["next_page"] = 0
			if context["page_obj"].has_next():
				object_json["has_next"] = True
				object_json["next_page"] = context["page_obj"].next_page_number()

			return HttpResponse(json.dumps(object_json), content_type='application/json')
		else:
			return super(Dashboard, self).render_to_response(context, **kwargs)


def homeredirect(request):
	if request.user.is_authenticated():
		if request.user.is_staff:
			if request.user.is_superuser:
				return HttpResponseRedirect("/user/list_all_user/")
			else:
				return HttpResponseRedirect("/user/profile/")
		else:
			return HttpResponseRedirect("/dashboard/")
	else:
		return HttpResponseRedirect("/accounts/login")


class FileListView(ListView):
	model = FileUpload

	def render_to_response(self, context, **response_kwargs):
		files = [serialize(p) for p in self.get_queryset()]
		group_forms = self.get_group_forms()
		error = "You do not have permission to upload your file. Please, contact you administrator"\
			if not self.request.user.user_profile.is_customer_superadmin else \
			"Your company haven't have any form yet! Please, contact administrator."

		data = {
			"files": {'files': files},
			"group_forms": group_forms,
			"error": error
		}
		response = JSONResponse(data, mimetype=response_mimetype(self.request))
		response['Content-Disposition'] = 'inline; filename=files.json'
		return response

	def get_queryset(self):
		now = datetime.datetime.now()
		start_date = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
		queryset = FileUpload.objects.filter(
			user_upload=self.request.user,
			upload_date__gt=start_date
		)
		return queryset

	def get_group_forms(self):
		user = self.request.user
		group_forms_json = []
		if user.user_profile.is_customer_superadmin:
			company_id = user.user_profile.company.id
			form = Form.objects.filter(company__id=company_id)

			group_form_object_check = {}
			items_selected = 0
			for f in form:
				try:
					index = group_form_object_check[str(f.groupform.id)]
					group_forms_json[index]["forms"].append({
						"id": f.id,
						"name": f.name
					})
				except KeyError:
					group_form_object = {}
					group_form = f.groupform
					group_form_object["id"] = group_form.id
					group_form_object["name"] = group_form.name
					group_form_object["forms"] = []
					group_form_object["forms"].append({
						"id": f.id,
						"name": f.name
					})
					group_forms_json.append(group_form_object)
					group_form_object_check[str(f.groupform.id)] = items_selected
					items_selected += 1
		else:
			company_id = user.user_profile.company.id
			_form = Form.objects.filter(company__id=company_id)

			if _form:
				forms_permission = User.objects.get(
					id=self.request.user.id
				).user_profile.permission.all()

				if forms_permission:
					user_permission_array = []
					for form_permission in forms_permission:
						user_permission_array.append(int(form_permission.id))

					form = Form.objects.filter(id__in=user_permission_array)

					group_form_object_check = {}
					items_selected = 0
					for f in form:
						try:
							index = group_form_object_check[str(f.groupform.id)]
							group_forms_json[index]["forms"].append({
								"id": f.id,
								"name": f.name
							})
						except KeyError:
							group_form_object = {}
							group_form = f.groupform
							group_form_object["id"] = group_form.id
							group_form_object["name"] = group_form.name
							group_form_object["forms"] = []
							group_form_object["forms"].append({
								"id": f.id,
								"name": f.name
							})
							group_forms_json.append(group_form_object)
							group_form_object_check[str(f.groupform.id)] = items_selected
							items_selected += 1
		return group_forms_json


upload_new = permission_access_page_required(FileCreateView.as_view())

upload_delete = permission_access_page_required(FileDeleteView.as_view())

upload_edit = permission_access_page_required(FileEditView.as_view())

upload_view = permission_access_page_required(FileListView.as_view())

upload_history = permission_access_page_required(HistoryUploadFile.as_view())
