================
 Change history
================

0.9.3
=====

*Unreleased*


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