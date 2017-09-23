from django.apps import apps
from django.contrib import admin

from zaakmagazijn.utils.admin import ReadOnlyModelAdmin

app = apps.get_app_config('rsgb')


for model_name, model in app.models.items():
    admin.site.register(model, ReadOnlyModelAdmin)
