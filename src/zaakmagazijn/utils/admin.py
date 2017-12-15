from django.contrib import admin

from zaakmagazijn.auditlog_extension.mixins import HistoryModelAdminMixin


class ReadOnlyModelAdminMixin:
    change_form_template = 'admin/readonly_change_form.html'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        """
        All fields are read only.
        """
        field_names = [f.name for f in self.model._meta.get_fields() if not f.auto_created or hasattr(f, 'through')]
        return field_names


class ReadOnlyModelAdmin(ReadOnlyModelAdminMixin, admin.ModelAdmin):
    pass


class ReadOnlyHistoryModelAdmin(ReadOnlyModelAdminMixin, HistoryModelAdminMixin, admin.ModelAdmin):
    pass
