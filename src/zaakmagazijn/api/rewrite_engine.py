from datetime import timedelta
from functools import WRAPPER_ASSIGNMENTS, wraps
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from lxml import etree

nsmap = {
    'zkn': 'http://www.egem.nl/StUF/sector/zkn/0310',
    'bg': 'http://www.egem.nl/StUF/sector/bg/0310',
    'stuf': 'http://www.egem.nl/StUF/StUF0301',
    'zds': 'http://www.stufstandaarden.nl/koppelvlak/zds0120',
    'soap11env': 'http://schemas.xmlsoap.org/soap/envelope/',
    'gml': 'http://www.opengis.net/gml',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}


class RewriteEngine:
    last_hit = None
    stp_tests = {}

    @staticmethod
    def remove_element(element, path):
        results = element.xpath(path, namespaces=nsmap)
        for result in results:
            result.getparent().remove(result)

    @classmethod
    def stp_rewrite_response_geefzaakdetails_zaklv01_1(cls, content):
        element = etree.fromstring(content)

        cls.remove_element(element, '//zkn:object/zkn:toelichting')
        cls.remove_element(element, '//zkn:object/zkn:publicatiedatum')
        cls.remove_element(element, '//zkn:object/zkn:einddatumGepland')
        cls.remove_element(element, '//zkn:object/zkn:uiterlijkeEinddatum')
        cls.remove_element(element, '//zkn:object/zkn:einddatum')
        cls.remove_element(element, '//zkn:object/zkn:betalingsIndicatie')
        cls.remove_element(element, '//zkn:object/zkn:laatsteBetaaldatum')
        cls.remove_element(element, '//zkn:object/zkn:archiefnominatie')
        cls.remove_element(element, '//zkn:object/zkn:datumVernietigingDossier')

        # TODO [KING]: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/geefzaakdetails-volgnummer-1-van-zds-12
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:achternaam')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:voorletters')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:voorvoegselAchternaam')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:geslachtsaanduiding')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:functie')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:datumUitDienst')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:omschrijving')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:toelichting')

        # TODO [TECH]: This hides an actual bug in our code.
        cls.remove_element(element, '//zkn:object/zkn:resultaat')

        cls.remove_element(element, '//zkn:object/zkn:heeft')

        return etree.tostring(element, encoding='utf8', xml_declaration=True, pretty_print=True)

    @classmethod
    def stp_rewrite_response_geefzaakdetails_zaklv01_5(cls, content):
        element = etree.fromstring(content)

        # TODO [KING]: https://discussie.kinggemeenten.nl/discussie/gemma/stuf-testplatform/geefzaakdetails-volgnummer-1-van-zds-12
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:achternaam')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:voorletters')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:voorvoegselAchternaam')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:geslachtsaanduiding')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:functie')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:gerelateerde/zkn:medewerker/zkn:datumUitDienst')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:omschrijving')
        cls.remove_element(element, '//zkn:object/zkn:heeftAlsInitiator/zkn:toelichting')

        return etree.tostring(element, encoding='utf8', xml_declaration=True, pretty_print=True)

    @classmethod
    def add_stuf_novalue(cls, root):
        # According to the StUF standard, all nil=True should also have attribute
        # noValue="geenWaarde"
        results = root.xpath('//*[@xsi:nil=\'true\']', namespaces=nsmap)
        for result in results:
            result.attrib['{http://www.egem.nl/StUF/StUF0301}noValue'] = 'geenWaarde'

    @classmethod
    def rewrite_response(cls, content):
        # Cleanup namespaces
        root = etree.fromstring(content)

        cls.add_stuf_novalue(root)

        # TODO [TECH]: This removes the ZDS namespace (since its the target
        # namespace) but we don't want that because the reference WSDL uses it.
        # etree.cleanup_namespaces(element, top_nsmap=nsmap)

        return etree.tostring(root, encoding='utf8', xml_declaration=True, pretty_print=True)

    @classmethod
    def rewrite(cls, view_func):
        def wrapped_view(*args, **kwargs):
            request = args[0]

            response = view_func(*args, **kwargs)
            response_content = response.content

            length = int(request.environ.get('CONTENT_LENGTH', '0') or 0)
            if settings.ZAAKMAGAZIJN_STUF_TESTPLATFORM and length > 0:
                request_content = request.environ['wsgi.input'].read(length)
                body = BytesIO(request_content)
                request.environ['wsgi.input'] = body
                test_name = etree.fromstring(request_content)[1][0].tag

                # strip namespace
                test_name = test_name[test_name.find('}') + 1:]

                test_name = test_name.lower()

                # Reset the test progress after five minutes of inactivity.
                current_time = timezone.now()
                if cls.last_hit and current_time - timedelta(minutes=5) > cls.last_hit:
                    cls.stp_tests = {}
                cls.last_hit = current_time

                cls.stp_tests.setdefault(test_name, 0)
                cls.stp_tests[test_name] += 1

                method_name = 'stp_rewrite_response_{test_name}_{i}'.format(
                    test_name=test_name, i=cls.stp_tests[test_name])
                method = getattr(cls, method_name, None)
                if method:
                    response_content = method(response.content)

                print('Incomming request: {} volgnummer {}{}'.format(
                    test_name,
                    cls.stp_tests[test_name] * 2 - 1,
                    ' (applied {})'.format(method_name) if method else '',
                ))

            response_content = cls.rewrite_response(response_content)
            new_response = HttpResponse(
                response_content, status=response.status_code, reason=response._reason_phrase,
            )

            # Copy over the headers.
            for key, value in response.items():
                # Content-Length should be recalculated.
                if key.lower() in ['content-length', ]:
                    continue
                new_response[key] = value

            # We could copy over cookies but it doesn't seem needed.

            return new_response

        return wraps(view_func, assigned=WRAPPER_ASSIGNMENTS)(wrapped_view)
