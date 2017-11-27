==============
Change history
==============

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
