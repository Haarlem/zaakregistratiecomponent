from zaakmagazijn.api.stuf.models import BinaireInhoud

from .client import default_client as dms_client


class DMSFieldDescriptor:

    def __init__(self, field_name, model):
        self.field_name = field_name

    def __get__(self, instance, cls=None):
        filename, inhoud = dms_client.geef_inhoud(instance)
        return {
            'data': inhoud,
            'bestandsnaam': filename
        }

    def __set__(self, instance, inhoud: BinaireInhoud):
        if inhoud is None:
            return

        dms_client.maak_zaakdocument(instance, filename=inhoud.bestandsnaam)
        content = inhoud.to_cmis()
        # TODO [TECH]: set bestandsnaam/contentType even if no data is present?
        if content is not None:
            dms_client.zet_inhoud(instance, content, inhoud.contentType)


class DMSField:
    """
    A virtual Django model field proxying to the underlying DMS.
    """
    is_relation = False
    remote_field = None
    concrete = False
    column = None
    null = True
    blank = True
    validators = ()
    primary_key = False
    auto_created = False

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def contribute_to_class(self, model, name):
        self.name = name
        self.attname = name
        self.verbose_name = "DMS Field"
        self.model = model
        model._meta.add_field(self, private=True)
        setattr(model, self.attname, DMSFieldDescriptor(self.attname, model))

    def has_default(self):
        return False
