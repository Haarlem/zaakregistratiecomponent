from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ..utils.admin import ReadOnlyModelAdmin
from .models import (
    Application, ApplicationGroup, Endpoint, Organisation, ServiceOperation
)


@admin.register(ServiceOperation)
class ServiceOperationAdmin(ReadOnlyModelAdmin):
    list_display = ('name', 'namespace', 'operation_name', )
    list_filter = ('namespace', )


@admin.register(ApplicationGroup)
class ApplicationGroupAdmin(admin.ModelAdmin):
    list_display = ('name', )
    filter_horizontal = ('service_operations', )


class EndpointInline(admin.TabularInline):
    model = Endpoint


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'organisation', 'get_groups_display', )
    list_filter = ('organisation', )
    filter_horizontal = ('groups', )
    inlines = (EndpointInline, )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('groups')

    def get_groups_display(self, obj):
        return ', '.join([g.name for g in obj.groups.all()])
    get_groups_display.short_description = _('groepen')


@admin.register(Organisation)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', )
