from django.contrib import admin


class ReadOnlyModelAdmin(admin.ModelAdmin):
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
