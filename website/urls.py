from django.conf.urls import patterns, url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from uploading.views import Dashboard, homeredirect

urlpatterns = patterns(
	"",
	url(r"^$", homeredirect),
	url(r'^admin/', include(admin.site.urls)),
	url(r"^dashboard", Dashboard.as_view(), name="dashboard"),
	url(r'^accounts/', include('allauth.urls')),
	url(r'^user/', include('userprofile.urls')),
	url(r'^upload/', include('uploading.urls')),
	url(r'^processing/', include('processing.urls')),
	url(r'^transaction/', include('transaction.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

#should remove url for customer