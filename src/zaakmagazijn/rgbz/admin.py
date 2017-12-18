from django.apps import apps
from django.contrib import admin

from auditlog.registry import auditlog

from zaakmagazijn.utils.admin import ReadOnlyHistoryModelAdmin

app = apps.get_app_config('rgbz')


for model_name, model in app.models.items():
    admin.site.register(model, ReadOnlyHistoryModelAdmin)
    # The "_inhoud" field is excluded because it retrieves data from the DMS.
    auditlog.register(model, exclude_fields=['_inhoud'])
