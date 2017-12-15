from django.apps import apps
from django.contrib import admin

from auditlog.registry import auditlog

from zaakmagazijn.utils.admin import ReadOnlyHistoryModelAdmin

app = apps.get_app_config('rsgb')


for model_name, model in app.models.items():
    admin.site.register(model, ReadOnlyHistoryModelAdmin)
    auditlog.register(model)
