from django.conf.urls import patterns, url
from processing.views import *;

urlpatterns = patterns(
	"",
	url(r"^input_data", input_data, name="input_data"),
	url(r"^save_data", save_data, name="save_data"),
	url(r"^update_status_tiff", update_status_tiff_file, name="update_status_tiff"),
)
