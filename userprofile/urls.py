from django.conf.urls import patterns, url
from userprofile.views import add_customer_admin, add_customer_staff, edit_customer_staff, add_staff, \
	edit_customer_admin, edit_staff, list_user, PermissionTemplate, MyProfile


urlpatterns = patterns(
	"",
	url(r"^staff_add", add_staff, name="add_staff"),
	url(r"^customer_admin_add", add_customer_admin, name="add_customer_admin"),
	url(r"^customer_staff_add", add_customer_staff, name="add_customer_staff"),
	url(r"^staff_edit/(?P<pk>\d+)", edit_staff, name="edit_staff"),
	url(r"^customer_admin_edit/(?P<pk>\d+)", edit_customer_admin, name="edit_customer_admin"),
	url(r"^customer_staff_edit/(?P<pk>\d+)", edit_customer_staff, name="edit_customer_staff"),
	url(r"^list_all_user", list_user, name="list_user"),
	url(r"^permission", PermissionTemplate.as_view(), name="permission"),
	url(r"^profile", MyProfile.as_view(), name="my-profile"),
	url(r"^get_menu_header", "userprofile.views.get_menu_header"),
	url(r"^get_notify_staff", "userprofile.views.get_notify_staff"),
)
