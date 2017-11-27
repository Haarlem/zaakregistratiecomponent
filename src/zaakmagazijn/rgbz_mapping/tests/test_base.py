from django.test import TestCase

from ..base import AutoMapper
from ..models import GemeenteObjectProxy


class AutoMapperTests(TestCase):
    def test_get_fields(self):
        auto_mapper = AutoMapper()
        auto_mapper.set_proxy_model(GemeenteObjectProxy)

        fields = {str(f) for f in auto_mapper}
        expected_fields = {
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: datum_einde_geldigheid_gemeente to datum_einde_geldigheid_gemeente>',
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: datum_begin_geldigheid_gemeente to datum_begin_geldigheid_gemeente>',
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: gemeentenaam to gemeentenaam>',
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: geometrie to geometrie>',
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: naam to naam>',
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: objecttype to objecttype>',
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: _objecttype_model to _objecttype_model>',
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: identificatie to identificatie>',
            '<zaakmagazijn.rgbz_mapping.base.ProxyField: id to id>'
        }
        self.assertEqual(fields, expected_fields)
