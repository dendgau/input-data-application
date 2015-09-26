from django.utils.translation import ugettext

def filesizeformat(bytes):
    try:
        bytes = float(bytes)
    except (TypeError,ValueError,UnicodeDecodeError):
        return u"0 bytes"

    if bytes < 1024:
        return ugettext("%(size)d byte", "%(size)d bytes", bytes) % {'size': bytes}
    if bytes < 1024 * 1024:
        return ugettext("%.1f KB") % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return ugettext("%.1f MB") % (bytes / (1024 * 1024))
    return ugettext("%.1f GB") % (bytes / (1024 * 1024 * 1024))