from django.contrib import admin

# Register your models here.
from uploading.models import *;

class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['name', 'note', 'file', 'form_name', 'upload_date', 'user_upload', 'process_date', 'user_process']
    list_filter = ['name', 'note', 'file', 'upload_date', 'user_upload', 'process_date', 'user_process']
    search_fields = ['name', 'note', 'file', 'form_name', 'upload_date', 'user_upload', 'process_date', 'user_process']
    sortable_field_name = "name"
    autocomplete_lookup_fields = {
        'name': ['name'],
    }

    def form_name(self, obj):
        return '%s'%(obj.form.name)
    form_name.short_description = 'Form name' #for column header
    def user_upload(self, obj):
        return '%s'%(obj.User.username)
    user_upload.short_description = 'User upload' #for column header    
    def user_process(self, obj):
        return '%s'%(obj.User.username)
    user_process.short_description = 'User process' #for column header   
    
admin.site.register(FileUpload, FileUploadAdmin)  

class FormFieldValueAdmin(admin.ModelAdmin):
    list_display = ['value', 'fileupload_name', 'formfield']
    list_filter = ['value', 'formfield']
    search_fields = ['value', 'fileupload_name', 'formfield']
    sortable_field_name = "value"
    autocomplete_lookup_fields = {
        'value': ['value'],
    }

    def fileupload_name(self, obj):
        return '%s'%(obj.fileupload.name)
    fileupload_name.short_description = 'File name' #for column header
    def formfield(self, obj):
        return '%s'%(obj.FormField.index)
    formfield.short_description = 'Index' #for column header

admin.site.register(FormFieldValue, FormFieldValueAdmin)  

class FileUploadGroupFieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'fileupload_name', 'groupfield']
    list_filter = ['id', 'groupfield']
    search_fields = ['id', 'fileupload_name', 'groupfield']
    sortable_field_name = "id"
    autocomplete_lookup_fields = {
        'id': ['id'],
    }

    def fileupload_name(self, obj):
        return '%s'%(obj.fileupload.name)
    fileupload_name.short_description = 'Name' #for column header

    def groupfield(self, obj):
        return '%s'%(obj.GroupField.name)
    groupfield.short_description = 'Group field name' #for column header    

admin.site.register(FileUploadGroupField, FileUploadGroupFieldAdmin)  

class FileUploadGroupFieldFieldValueAdmin(admin.ModelAdmin):
    list_display = ['value', 'fileuploadgroupfield', 'groupfieldfield']
    list_filter = ['value', 'fileuploadgroupfield', 'groupfieldfield']
    search_fields = ['value', 'fileuploadgroupfield', 'groupfieldfield']
    sortable_field_name = "value"
    autocomplete_lookup_fields = {
        'value': ['value'],
    }

    def fileuploadgroupfield(self, obj):
        return '%s'%(obj.FileUploadGroupField.id)
    fileuploadgroupfield.short_description = 'File upload group field ID' #for column header

    def groupfieldfield(self, obj):
        return '%s'%(obj.GroupFieldField.index)
    groupfieldfield.short_description = 'Group field field Index' #for column header    

admin.site.register(FileUploadGroupFieldFieldValue, FileUploadGroupFieldFieldValueAdmin)

class WarningUploadAdmin(admin.ModelAdmin):
    list_display = ['content_error', 'fileupload_name']
    list_filter = ['content_error', ]
    search_fields = ['content_error', 'fileupload_name']
    sortable_field_name = "content_error"
    autocomplete_lookup_fields = {
        'content_error': ['content_error'],
    }

    def fileupload_name(self, obj):
        return '%s'%(obj.FileUpload.name)
    fileupload_name.short_description = 'File name' #for column header

admin.site.register(WarningUpload, WarningUploadAdmin)  

class FileTiffAdmin(admin.ModelAdmin):
    list_display = ['name', 'path', 'status', 'page_index', 'fileupload_name']
    list_filter = ['name', 'path', 'status', 'page_index', ]
    search_fields = ['name', 'path', 'status', 'page_index', 'fileupload_name']
    sortable_field_name = "name"
    autocomplete_lookup_fields = {
        'name': ['name'],
    }

    def fileupload_name(self, obj):
        return '%s'%(obj.fileupload.name)
    fileupload_name.short_description = 'Uploaded file' #for column header

admin.site.register(FileTiff, FileTiffAdmin)

