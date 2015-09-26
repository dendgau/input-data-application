from functools import wraps
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import available_attrs
from django.utils.six.moves.urllib.parse import urlparse
from django.shortcuts import resolve_url

BACK_LINK = "/user/profile/"

PERMISSION_ACCESS_PAGE_CONFIG = {
	"admin": {
		"add_staff": "add_staff",
		"edit_staff": "edit_staff",
		"add_customer_admin": "add_customer_admin",
		"edit_customer_admin": "edit_customer_admin",
		"edit_customer_staff": "edit_customer_staff",
		"list_user": "list_user",
		"group-form-add": "group-form-add",
		"group-form-edit": "group-form-edit",
		"field-add": "field-add",
		"field-edit": "field-edit",
		"list-field": "list-field",
		"list-group-form": "list-group-form",
		"field-delete": "field-delete",
		"group-form-delete": "group-form-delete",
		"groupfield_list": "groupfield_list",
		"form_list": "form_list"
	},
	"staff": {
		"transaction-files": "transaction-files"
	},
	"customer_admin": {
		"add_customer_staff": "add_customer_staff",
		"edit_customer_staff": "edit_customer_staff",
		"list_user": "list_user",
		"upload-new": "upload-new",
		"upload-delete": "upload-delete",
		"upload-edit": "upload-edit",
		"upload-view": "upload-view",
		"upload-history": "upload-history"
	},
	"customer_staff": {
		"upload-new": "upload-new",
		"upload-delete": "upload-delete",
		"upload-edit": "upload-edit",
		"upload-view": "upload-view",
		"upload-history": "upload-history"
	},
}

def get_permission_user(user):
	if user.is_superuser:
		return "admin"

	if user.is_staff:
		return "staff"

	if user.user_profile.is_customer_superadmin:
		return "customer_admin"

	return "customer_staff"

def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):

	def decorator(view_func):
		@wraps(view_func, assigned=available_attrs(view_func))
		def _wrapped_view(request, *args, **kwargs):
			if test_func(request.user):
				permission = get_permission_user(request.user)
				from django.core.urlresolvers import resolve
				current_url = resolve(request.path_info).url_name
				try:
					is_permission = PERMISSION_ACCESS_PAGE_CONFIG[permission][current_url]
				except KeyError:
					return HttpResponsePermanentRedirect(BACK_LINK)
				return view_func(request, *args, **kwargs)

			path = request.build_absolute_uri()
			resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
			# If the login url is the same scheme and net location then just
			# use the path as the "next" url.
			login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
			current_scheme, current_netloc = urlparse(path)[:2]
			if ((not login_scheme or login_scheme == current_scheme) and
					(not login_netloc or login_netloc == current_netloc)):
				path = request.get_full_path()
			from django.contrib.auth.views import redirect_to_login
			return redirect_to_login(
				path, resolved_login_url, redirect_field_name)
		return _wrapped_view
	return decorator


def permission_access_page_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):

	actual_decorator = user_passes_test(
		lambda u: u.is_authenticated(),
		login_url=login_url,
		redirect_field_name=redirect_field_name
	)
	if function:
		return actual_decorator(function)
	return actual_decorator
