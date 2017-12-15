from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from auditlog.admin import LogEntryAdmin
from auditlog.models import LogEntry


class LogEntryAdminExt(LogEntryAdmin):
    change_form_template = 'admin/readonly_change_form.html'

    list_display = ['created', 'resource_url', 'get_action_display', 'msg_short', 'get_user_display']
    search_fields = ['timestamp', 'object_repr', 'changes', 'actor__first_name', 'actor__last_name', 'additional_data']
    readonly_fields = ['created', 'resource_url', 'get_action_display', 'get_user_display', 'msg', 'additional_data']
    fieldsets = [
        (None, {'fields': ['created', 'get_user_display', 'resource_url']}),
        (_('Changes'), {'fields': ['get_action_display', 'msg']}),
        # (_('Additional data'), {'fields': ['additional_data']}),
    ]

    def get_action_display(self, obj):
        if obj.additional_data and 'functie' in obj.additional_data:
            return obj.additional_data['functie']
        return obj.get_action_display()
    get_action_display.allow_tags = True
    get_action_display.short_description = _('Action')

    def get_user_display(self, obj):
        if obj.additional_data and 'zender' in obj.additional_data:
            if obj.additional_data['zender']:
                return ', '.join(['<strong>{}</strong>: {}'.format(
                    k, v if v else '(onbekend)') for k, v in obj.additional_data['zender'].items()]
                )
            else:
                return '(onbekend)'
        return self.user_url(obj)
    get_user_display.allow_tags = True
    get_user_display.short_description = _('User')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.unregister(LogEntry)
admin.site.register(LogEntry, LogEntryAdminExt)
