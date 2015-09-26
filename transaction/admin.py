from django.contrib import admin
from transaction.models import *

admin.site.register(FieldType)
    
class FieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'fieldtype', 'description', 'html']
    list_filter = ['label', 'fieldtype', 'description', 'html']
    search_fields = ['label', 'fieldtype', 'description', 'html']
    sortable_field_name = "lable"
    autocomplete_lookup_fields = {
        'label': ['label'],
    }

    def fieldtype(self, obj):
        return '%s'%(obj.FieldType.name)
    fieldtype.short_description = 'Type' #for column header
    #field_type.admin_order_field = 'FieldType__name' #for ordering
admin.site.register(Field, FieldAdmin)  

admin.site.register(GroupField)

class GroupFieldFieldAdmin(admin.ModelAdmin):
    model = GroupFieldField
    list_display = ['index', 'field', 'groupfield']
    list_filter = ['index', 'field', 'groupfield']
    search_fields = ['index', 'field', 'groupfield']
    sortable_field_name = "index"
    autocomplete_lookup_fields = {
        'index': ['index'],
    }

    def field(self, obj):
        return '%s'%(obj.Field.label)
    field.short_description = 'Field label' #for column header
    
    def groupfield(self, obj):
        return '%s'%(obj.GroupField.name)
    groupfield.short_description = 'Group field name' #for column header

admin.site.register(GroupFieldField, GroupFieldFieldAdmin)  

class GroupFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'html', 'icon']
    list_filter = ['name', 'description', 'html', 'icon']
    search_fields = ['name', 'description', 'html', 'icon']
    sortable_field_name = "name"
    autocomplete_lookup_fields = {
        'name': ['name'],
    }
admin.site.register(GroupForm, GroupFormAdmin)  

class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['index', 'field', 'form_name']
    list_filter = ['index', 'field', ]
    search_fields = ['index', 'field', 'form_name']
    sortable_field_name = "index"
    autocomplete_lookup_fields = {
        'index': ['index'],
    }

    def field(self, obj):
        return '%s'%(obj.Field.label)
    field.short_description = 'Field label' #for column header
    
    def form_name(self, obj):
        return '%s'%(obj.form.name)
    form_name.short_description = 'Form name' #for column header
    #field_type.admin_order_field = 'FieldType__name' #for ordering
admin.site.register(FormField, FormFieldAdmin)  

class FormGroupFieldAdmin(admin.ModelAdmin):
    list_display = ['index', 'groupfield', 'form_name']
    list_filter = ['index', 'groupfield', ]
    search_fields = ['index', 'groupfield', 'form_name']
    sortable_field_name = "index"
    autocomplete_lookup_fields = {
        'index': ['index'],
    }

    def groupfield(self, obj):
        return '%s'%(obj.GroupField.name)
    groupfield.short_description = 'Group field name' #for column header
    
    def form_name(self, obj):
        return '%s'%(obj.form.name)
    form_name.short_description = 'Form name' #for column header
    #field_type.admin_order_field = 'FieldType__name' #for ordering
admin.site.register(FormGroupField, FormGroupFieldAdmin)  

class FormAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'groupform']
    list_filter = ['name', 'company', 'groupform']
    search_fields = ['name', 'company', 'groupform']
    sortable_field_name = "name"
    autocomplete_lookup_fields = {
        'name': ['name'],
    }

    def company(self, obj):
        return '%s'%(obj.Company.full_name)
    company.short_description = 'Company name' #for column header

    def groupform(self, obj):
        return '%s'%(obj.GroupForm.name)
    groupform.short_description = 'Group form name' #for column header    
    #field_type.admin_order_field = 'FieldType__name' #for ordering
admin.site.register(Form, FormAdmin)  
