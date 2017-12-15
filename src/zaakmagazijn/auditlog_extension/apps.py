from django.apps import AppConfig


class AuditLogExtConfig(AppConfig):
    name = 'zaakmagazijn.auditlog_extension'
    verbose_name = "Audit log extension"

    def ready(self):
        from . import signals  # noqa
