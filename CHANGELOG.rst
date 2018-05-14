==============
Change history
==============

0.9.10
======

*tbd*

* Fixed ``link`` in the RGBZ compatability layer to actually return the the
  ``link`` value of ``InformatieObject``en in related services. It previously
  returned the ``formaat`` value by mistake.
* Fixed issues with fields ``vertrouwlijkAanduiding`` and
  ``vertrouwelijkheidAanduiding``. The ZDS 1.2 specification contains invalid
  attribute names. These fields are now all named ``vertrouwelijkAanduiding``.


0.9.9
=====

*April 20, 2018*

* Fixed ``geslachtsaanduiding`` en ``geboortedatum`` to be optional for a
  ``NatuurlijkPersoon``.
* Fixed issues with fields ``vertrouwlijkAanduiding`` and
  ``vertrouwelijkheidAanduiding``. The ZDS 1.2 specification contains invalid
  attribute names. These fields are now all named ``vertrouwelijkAanduiding``.


0.9.8
=====

*April 9, 2018*

* Removed the need to double-encode ``inhoud`` for ``updateZaakdocument`` and
  ``voegZaakdocumentToe``. If you double encoded the content, you should
  remove this behaviour when you update to this version. Otherwise, the
  documents in your DMS will be unreadable (that is, base64 encoded).


0.9.7
=====

*December 22, 2017*

* Fixed an issue with some ``sortering`` options not being properly populated
  through the RGBZ compatability layer, resulting in an error.
* Fixed various issues related to the WSDL rendering when
  ``ZAAKMAGAZIJN_REFERENCE_WSDL`` is set to ``False``. It can now be parsed by
  SoapUI again.
* Fixed various small issues.
* Pointed README shields to Haarlem repository.


0.9.6
=====

*December 18, 2017*

* Added audit log to the admin interface.
* The intended receiver ("ontvanger") is now checked even when
  ``ZAAKMAGAZIJN_OPEN_ACCESS`` is ``True``.
* Fixed ``CMIS_SENDER_PROPERTY`` which was not used at all.


0.9.5
=====

*December 14, 2017*

* Fixed issue where the default value for XSD elements were seen as "provided"
  by the request. This lead to incorrect lookups.
* Restored validation of the incoming requests again. This was accidentally
  removed to work with the StUF testplatform in 0.9.4. Note that with the
  introduction of the KING reference WSDL, this validation is much more
  strict.
* Altered the ``voegZaakdocumentToe`` service to create a document in a single
  action instead of 2 (create document, add content to document). This
  deviates from the specification but prevents documents starting at version
  1.1. Documents in the DMS now start at version 1.0.
* Added the "stuurgegevens/zender" information to a custom DMS property. This
  property can be configured with ``CMIS_SENDER_PROPERTY`` and should be a
  ``string``, or ``None`` if no sender property is present.


0.9.4
=====

*November 28, 2017*

* Added compatibility layer between ZDS 1.2 and RGBZ 2.0 that mimics an RGBZ
  1.0 data model. This resolves *most* compliancy issues with ZDS 1.2.
* Added full support for test messages from the StUF test platform. This makes
  copying tests from the StUF test platform easier.
* Added pre- and post processing to requests and responses to overcome issues
  with the StUF test platform.
* Added ZDS 1.2 compliancy test run, as performed by the StUF test platform.
* Added the KING reference WSDL and used this by default (instead of the
  generated version).
* Changed the WSDL endpoint ``Beantwoordvraag`` to ``BeantwoordVraag``, as per
  specification. A redirect was added for convenience.
* Added management command ``create_test_data`` to load the test data set
  needed for the StUF test platform.
* Fixed incorrect ``overdragenZaak`` message.
* Various minor fixes to comply with the StUF test platform.
* Added new setting ``ZAAKMAGAZIJN_REFERENCE_WSDL`` (defaults to ``True``)
  indicating whether to use the KING reference WSDL. If ``False``, the
  generated WSDL is used.
* Added new setting ``ZAAKMAGAZIJN_STUF_TESTPLATFORM`` (defaults to
  ``False``) indicating whether to use the StUF test platform workarounds.
  This should only be used when setting up an environment to test against the
  StUF test platform.
* Added new setting ``ZAAKMAGAZIJN_URL`` which should be the URL where the
  Zaakmagazijn's WSDL is served. For example: http://www.example.com


0.9.3
=====

*November 24, 2017*

* Fixed CMIS-lib issue that caused large file uploads to cause an exception.
* Fixed issue where multiple InformatieObjectType could have the same
  description.
* Fixed missing Redis installation in CentOS setup script.
* Updated to Django 1.11.7.
* Improved documentation.
* Removed incorrect mention of PyPy support.


0.9.2
=====

*October 19, 2017*

* Added new setting ``ZAAKMAGAZIJN_ZAAK_ID_GENERATOR`` which takes a function
  to generate a unique ID for ``genereerZaakIdentificatie_Di02``.
* Added a new unique ID generator with a simple incremental number, prefixed
  by the current year (for example: 2017-0000001):
  ``zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_id``
* Documented previously undocumented Zaakmagazijn settings.
* Removed the DMS mapping of the property ``handelsnaam`` that did not exist
  in the content model.
* Updated CentOS install documentation.
* Updated the alternative DMS tree structure to start in the ``Sites`` >
  ``archief`` directory.


0.9.1
=====

*September 29, 2017*

* Fixed incorrect document identifier for filtering documents.
* Fixed ``EmptyResultError`` being thrown while instead an empty result should
  just be returned.
* Increased maximum allowed request size to allow large ``inhoud`` field
  contents, up to ~22 MB.


0.9
===

*September 26, 2017*

* Initial public release.
