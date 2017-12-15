from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect
from django.urls import reverse


class HistoryModelAdminMixin:
    def history_view(self, request, object_id, extra_context=None):
        return HttpResponseRedirect(
            '{url}?resource_type={content_type}&object_id={object_id}'.format(
                url=reverse("admin:auditlog_logentry_changelist", args=()),
                content_type=ContentType.objects.get_for_model(self.model).pk,
                object_id=object_id,
            )
        )


class HistoryModelAdmin(HistoryModelAdminMixin):
    pass
