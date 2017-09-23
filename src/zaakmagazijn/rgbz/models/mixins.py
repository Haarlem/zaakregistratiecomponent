from django.core.exceptions import ValidationError
from django.db import models

from ...utils import stuf_datetime
from ...utils.fields import StUFDateTimeField
from ..choices import GeslachtsAanduiding
from ..validators import validate_non_negative_string


class TijdstipRegistratieMixin(models.Model):
    tijdstip_registratie = StUFDateTimeField(default=stuf_datetime.now)

    class Meta:
        abstract = True


class TypeMixin(models.Model):
    """
    A mechanism to save the type (mnemonic) and/or the name of the model.
    """

    def _get_parent_ptr_name(self, class_name):
        return '{}_ptr'.format(class_name.lower())

    def _determine_type(self, class_name, field_name):
        """
        From a field saved on the model determine the type, and retrieve the object of that type.

        Note that this can go several layers deep, you can have many layers of model inheritance
        where every layer saves the name of the submodel, following that chain you can determine
        from the top model, the lowest model.

        :param class_name Name of the parent model class
        :param field_name The field name where the model name is stored on
        :return obj Child object of this object, or self no lower model was stored.
        """
        ptr_name = self._get_parent_ptr_name(class_name)
        # Instead of going over all possible child relations, get the stored child model name and only retrieve that
        # relation.
        if hasattr(self, ptr_name):
            return self
        if not getattr(self, field_name):
            return self

        obj = getattr(self, getattr(self, field_name).lower())
        if hasattr(obj, 'is_type'):
            return obj.is_type()
        else:
            return obj

    def _save_child_model(self, class_name, field_name):
        """
        Save the name of the child model in this model, so that it is possible, without
        iterating over all child relations to determine what kind of type this is, and look it up.

        :param class_name Name of the parent model class
        :param field_name The field name where the model name will be stored.
        """
        ptr_name = self._get_parent_ptr_name(class_name)
        if hasattr(self, ptr_name):
            obj = getattr(self, ptr_name)
            cls = type(obj)

            type_child_model = self.__class__
            # If type_child_model is a _direct_ subclass of this class, save the model name
            # If, there is model inheritance which is three (or more) levels deep
            # the model name of the third level should be saved in the second level.
            if type_child_model in cls.__subclasses__():
                setattr(obj, field_name, type_child_model.__name__)
                obj.save()

    def _save_type(self, class_name, field_name):
        """
        Save the mnemonic of the furthest child to in the model. This is used
        to be able to set a unique constraint on this field, plus some identifier,
        uniquely identifying this type of object.

        :param class_name Name of the parent model class
        :param field_name The field name where the mnemonic will be stored.
        """
        ptr_name = self._get_parent_ptr_name(class_name)

        if hasattr(self, ptr_name):
            obj = getattr(self, ptr_name)
            child_obj = self.is_type()
            if child_obj and hasattr(child_obj._meta, 'mnemonic'):
                setattr(obj, field_name, child_obj._meta.mnemonic)
                obj.save()

    class Meta:
        abstract = True


class ExtraValidatorsMixin(models.Model):
    """
    A list of validators, which shouldn't be picked up by migrations, but
    should be run on full_clean. This type of validation is used to deal
    with field which are defined in the parent model, with model inheritance,
    but where we don't want to re-define the fields on the inheriting model.

    In EXTRA_VALIDATORS, specify a dictionary with field names as keys, and
    a list of validators as values.
    """
    EXTRA_VALIDATORS = {}

    def clean_fields(self, exclude=None):
        errors = {}
        for field_name, validators in self.EXTRA_VALIDATORS.items():
            for validator in validators:
                try:
                    validator(getattr(self, field_name))
                except ValidationError as e:
                    errors[field_name] = e.error_list

        try:
            super().clean_fields(exclude=exclude)
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    class Meta:
        abstract = True


class BSNMixin(models.Model):
    """
    Mixin voor een Burgerservicenummer veld, opgenomen als mixin om redudantie te voorkomen.

    Alle nummers waarvoor geldt dat, indien aangeduid als (s0 s1 s2 s3 s4
    s5 s6 s7 s8), het resultaat van (9*s0) + (8*s1) + (7*s2) +...+ (2*s7) -
    (1*s8) deelbaar is door elf.
    """
    burgerservicenummer = models.CharField(max_length=9, validators=[validate_non_negative_string, ],
                                           help_text='Het burgerservicenummer, bedoeld in artikel 1.1 van de Wet algemene bepalingen burgerservicenummer.')

    class Meta:
        abstract = True


class RekeningnummerMixin(models.Model):
    """
    Mixin voor een Foreignkey verwijzend naar een Rekeningnummer object.
    """
    rekeningnummer = models.ForeignKey(
        'rgbz.Rekeningnummer', on_delete=models.CASCADE, null=True, blank=True,
        help_text='De gegevens inzake de bankrekening waarmee het SUBJECT in de regel financieel communiceert.'
    )

    class Meta:
        abstract = True


class GeslachtsAanduidingMixin(models.Model):
    geslachtsaanduiding = models.CharField(
        max_length=1, help_text='Een aanduiding die aangeeft of de persoon een man of een vrouw is, '
                                'of dat het geslacht nog onbekend is.', choices=GeslachtsAanduiding.choices)

    class Meta:
        abstract = True


class AfwijkendeCorrespondentieMixin(models.Model):
    afwijkend_binnenlands_correspondentieadres = models.ForeignKey(
        'rsgb.AdresMetPostcode', on_delete=models.SET_NULL, null=True, blank=True)
    afwijkend_correspondentie_postadres = models.ForeignKey(
        'rsgb.PostAdres', on_delete=models.SET_NULL, null=True, blank=True)
    afwijkend_buitenlands_correspondentieadres = models.ForeignKey(
        'rsgb.VerblijfBuitenland', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True
