from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from uploading.models import *;
from transaction.models import *;
from operator import itemgetter
import datetime
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages


# prepare form
def input_data(request):
	if request.method == 'GET':
		#user process
		current_user = request.user
		user_id = current_user.id
		#pdf file
		fileupload_id = request.GET['fileupload_id']
		form_id = request.GET['form_id']
		#FileUpload matching query does not exist.

		#check permission
		forms_permission = User.objects.get(id=request.user.id).user_profile.permission.all()
		#QuerySet: [<Form: Com4 - Invoice 1>, <Form: Com4 - Bill>]
		is_granted = False
		if request.user.is_staff:
			for form_permission in forms_permission:
				if str(form_permission.id) == str(form_id):
					is_granted = True
					break

		#end check permission
		if is_granted == False:
			messages.add_message(request, messages.ERROR, 'You do not have permission to process the form')
			return HttpResponseRedirect('/accounts/login')
		else:

			#check if file does not exist then return the error
			file = FileUpload.objects.get(id=fileupload_id)

			form = file.form

			fileupload_note = file.note

			#get groupfield of the form
			groupfield = None
			try:
				groupfield = GroupField.objects.get(formgroupfield__form=form) #have groupfield
			except GroupField.DoesNotExist:
				groupfield = None   #does not have groupfield
			#if have groupfield, send GroupFieldField to the response
			groupfield_fields = []
			groupfield_index = -1
			groupfield_id = -1
			if groupfield:
				formgroupfield = FormGroupField.objects.get(form = form, groupfield=groupfield)
				groupfield_index = formgroupfield.index
				groupfield_id = formgroupfield.id
				groupfieldfields = GroupFieldField.objects.filter(groupfield=groupfield).order_by('index')
				for groupfieldfield in groupfieldfields:
					dic = {}
					dic["index"] = groupfieldfield.index
					field = groupfieldfield.field
					dic["id"] = field.id
					dic["label"] = field.label
					dic["description"] = field.description
					dic["html"] = field.html
					dic["fieldtype"] = field.fieldtype.name
					groupfield_fields.append(dic)

			#get tiff files and send to the response
			tiff_files = []
			filetiffs = FileTiff.objects.filter(fileupload=file).order_by('page_index')
			if filetiffs:
				for filetiff in filetiffs:
					dic = {}
					dic["id"] = filetiff.id
					dic["name"] = filetiff.name
					dic["path"] = filetiff.path
					dic["status"] = filetiff.status
					dic["page_index"] = filetiff.page_index
					tiff_files.append(dic)

			#get form fields and send to the response
			form_fields = []
			formfields = FormField.objects.filter(form=form).order_by('index')
			if formfields:
				for formfield in formfields:
					dic = {}
					dic["index"] = formfield.index
					field = formfield.field
					dic["id"] = field.id
					dic["label"] = field.label
					dic["description"] = field.description
					dic["html"] = field.html
					dic["fieldtype"] = field.fieldtype.name
					form_fields.append(dic)

			#check to see if data has been input or not
			#if yes load data to template

			#check value
			formfield_values = []
			formfieldvalues = FormFieldValue.objects.filter(fileupload = file)
			if formfieldvalues:
				for formfieldvalue in formfieldvalues:
					#field value & formfield index
					dic = {}
					dic["value"] = formfieldvalue.value
					dic["index"] = formfieldvalue.formfield.index
					dic["fieldtype"] = formfieldvalue.formfield.field.fieldtype.name
					formfield_values.append(dic)

			fileuploadgroupfields_count = 0
			fileuploadgroupfields_index = 0
			fileuploadgroupfieldfield_values = []
			fileuploadgroupfields = FileUploadGroupField.objects.filter(fileupload = file)
			if fileuploadgroupfields:
				for fileuploadgroupfield in fileuploadgroupfields:
					fileuploadgroupfields_count = fileuploadgroupfields_count + 1
					fileuploadgroupfieldfieldvalues = FileUploadGroupFieldFieldValue.objects.filter(fileuploadgroupfield = fileuploadgroupfield)
					for fileuploadgroupfieldfieldvalue in fileuploadgroupfieldfieldvalues:
						dic = {}
						dic["groupfield_index"] = fileuploadgroupfields_index
						dic["value"] = fileuploadgroupfieldfieldvalue.value
						dic["index"] = fileuploadgroupfieldfieldvalue.groupfieldfield.index
						dic["fieldtype"] = fileuploadgroupfieldfieldvalue.groupfieldfield.field.fieldtype.name
						fileuploadgroupfieldfield_values.append(dic)
					fileuploadgroupfields_index = fileuploadgroupfields_index + 1
			#don't need to check fileuploadgroupfields when send to template
			fileuploadgroupfields_range = range(0 , fileuploadgroupfields_count)
			groupfield_fields_range = range(0, len(groupfield_fields))

			file_tiff = FileTiff.objects.filter(fileupload__id=fileupload_id)
			file_tiff_process = FileTiff.objects.filter(
				fileupload__id=fileupload_id,
				status=1
			)

			if len(file_tiff_process) < len(file_tiff):
				messages.add_message(
					request,
					messages.WARNING,
					"WARNING: There are %s files have not processed yet" % str(len(file_tiff) - len(file_tiff_process))
				)

			if (len(formfield_values) > 0) or (len(fileuploadgroupfieldfield_values) > 0):
				return render_to_response('update_data.html', {'fileupload_id': fileupload_id,
														   'groupfield_index': groupfield_index,
														   'groupfield_id': groupfield_id,
														   'groupfield_fields': groupfield_fields,
														   'tiff_files': tiff_files,
														   'form_fields': form_fields,
														   'formfield_values': formfield_values,
														   'fileuploadgroupfields_count': fileuploadgroupfields_count,
														   'fileuploadgroupfields_range': fileuploadgroupfields_range,
														   'groupfield_fields_range': groupfield_fields_range,
														   'fileuploadgroupfieldfield_values': fileuploadgroupfieldfield_values,
														   'form_id': form_id,
														   'fileupload_note': fileupload_note,},
									  context_instance=RequestContext(request))
			else:
				return render_to_response('input_data.html', {'fileupload_id': fileupload_id,
														   'groupfield_index': groupfield_index,
														   'groupfield_id': groupfield_id,
														   'groupfield_fields': groupfield_fields,
														   'tiff_files': tiff_files,
														   'form_fields': form_fields,
														   'form_id': form_id,
														   'fileupload_note': fileupload_note, },
										context_instance=RequestContext(request))
#save data
@csrf_exempt 
def save_data(request):
	if request.method == "POST":
		form_id = request.POST['form_id']
		page_index = request.POST['page_index']
		user_process = request.user
		user_process_id = user_process.id

		#check permission
		forms_permission = User.objects.get(id=request.user.id).user_profile.permission.all()
		#QuerySet: [<Form: Com4 - Invoice 1>, <Form: Com4 - Bill>]
		is_granted = False
		if request.user.is_staff:
			for form_permission in forms_permission:
				if str(form_permission.id) == str(form_id):
					is_granted = True
					break

		#end check permission
		if is_granted == False:
			messages.add_message(request, messages.ERROR, 'You do not have permission to process the form')
			return HttpResponseRedirect('/accounts/login')
		else:
			#loop through POST parameters and seperate groupfield and formfield
			no_item = 0
			no_field_in_item = 0
			groupfield_items = []
			form_fields = []
			groupfield_items_sorted = []
			form_fields_sorted = []

			for key in request.POST:
				if 'groupfielditem_' in str(key):
					dic = {}
					dic["key"] = str(key)
					dic["value"] = request.POST[key]
					groupfield_items.append(dic)
				if 'formfield_' in str(key):
					dic = {}
					dic["key"] = str(key)
					dic["value"] = request.POST[key]
					form_fields.append(dic)
			if len(groupfield_items) > 0:
				groupfield_items_sorted = sorted(groupfield_items, key=itemgetter('key'))
				groupfield_items_sorted_len = len(groupfield_items_sorted)

				first_groupfield_item_no = ""
				first_groupfield_field = groupfield_items_sorted[0]
				first_groupfield_field_key = first_groupfield_field.get('key')
				substrings = first_groupfield_field_key.split('_')
				first_groupfield_item_no = substrings[1]

				for groupfield_item_sorted in groupfield_items_sorted:
					groupfield_item_sorted_key = groupfield_item_sorted.get('key')
					substrings = groupfield_item_sorted_key.split('_')
					groupfield_item_no = substrings[1]
					if first_groupfield_item_no == groupfield_item_no:
						no_field_in_item = no_field_in_item + 1
				no_item = len(groupfield_items_sorted)/no_field_in_item

			if len(form_fields) > 0:
				form_fields_sorted = sorted(form_fields, key=itemgetter('key'))

			fileupload = FileUpload.objects.get(id=request.POST['fileupload_id'])
			form = fileupload.form
			groupform = form.groupform

			#check to see if data has been input or not
			#if yes then delete data before saving

			#check value & deleting data
			check_formfieldvalues = FormFieldValue.objects.filter(fileupload = fileupload)
			check_fileuploadgroupfields = FileUploadGroupField.objects.filter(fileupload = fileupload)

			for check_fileuploadgroupfield in check_fileuploadgroupfields:
				check_fileuploadgroupfieldfieldvalues = FileUploadGroupFieldFieldValue.objects.filter(fileuploadgroupfield = check_fileuploadgroupfield)
				if len(check_fileuploadgroupfieldfieldvalues) > 0:
					check_fileuploadgroupfieldfieldvalues.delete()
			if len(check_fileuploadgroupfields) > 0:
				check_fileuploadgroupfields.delete()
			if len(check_formfieldvalues) > 0:
				check_formfieldvalues.delete()
			#end checking data & deleting data

			#save formfield value to database
			if len(form_fields) > 0:
				for field in form_fields_sorted:
					substrings = field.get('key').split('_')
					field_index = substrings[1]
					formfield = FormField.objects.filter(form=form).get(index = field_index)
					formfieldvalue = FormFieldValue(value = field.get('value'), fileupload = fileupload, formfield = formfield)
					formfieldvalue.save()

			#save groupfield and groupfieldfieldvalue to database
			if len(groupfield_items) > 0:
				formgroupfield = FormGroupField.objects.get(form = form)
				groupfield = formgroupfield.groupfield
				for i in range(0, no_item):
					fileuploadgroupfield = FileUploadGroupField(fileupload = fileupload, groupfield = groupfield)
					fileuploadgroupfield.save()
					for j in range(0,no_field_in_item):
						groupfieldfield_dic = groupfield_items_sorted[j+no_field_in_item*i]
						groupfieldfield_value = groupfieldfield_dic.get('value')
						groupfieldfield = GroupFieldField.objects.get(groupfield = groupfield, index = j)
						fileuploadgroupfieldfieldvalue = FileUploadGroupFieldFieldValue(value = groupfieldfield_value, fileuploadgroupfield = fileuploadgroupfield, groupfieldfield = groupfieldfield)
						fileuploadgroupfieldfieldvalue.save()

			#save user_process and process date to fileupload
			fileupload.user_process = user_process
			fileupload.process_date = datetime.datetime.now()
			fileupload.save()
			#done saving

			return HttpResponseRedirect('/processing/input_data?fileupload_id=%s&form_id=%s&page_index=%s'
										% (request.POST['fileupload_id'], form_id, page_index))

def update_status_tiff_file(request):
	if "fileupload_id" in request.POST:
		fileupload_id = int(request.POST.get("fileupload_id"))
		fileupload = FileUpload.objects.get(id=fileupload_id)
		permission_form = request.user.user_profile.permission.get(id=fileupload.form.id)

		if permission_form:
			fileupload.user_process = request.user
			fileupload.process_date = datetime.datetime.now()
			fileupload.save()

			file_tiff_id = int(request.POST.get("tiff_file_id"))
			file_tiff = FileTiff.objects.get(
				id=file_tiff_id,
				fileupload_id=fileupload_id
			)
			if file_tiff:
				file_tiff.status = 1
				file_tiff.save()
				return HttpResponse('')
			else:
				return HttpResponse(status=404)
