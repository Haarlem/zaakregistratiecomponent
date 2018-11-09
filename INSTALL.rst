===========
Installatie
===========

Het Zaakmagazijn is ontwikkeld in Python met behulp van het
`Django framework <https://www.djangoproject.com/>`_ en
`Spyne <http://spyne.io>`_.

Voor platform specifieke installatie instructies, zie de folder
"deployment".


Voorwaarden
===========

De volgende programma's of bibliotheken dienen aanwezig te zijn:

* Python 3.4 of hoger
* Python Virtualenv en Pip
* PostgreSQL 9.1 of hoger
* Vagrant (voor ontwikkeldoeleinden)


Instellingen
============

Alle instellingen van het Zaakmagazijn bevinden zich in
``src/zaakmagazijn/conf``. Het bestand ``local.py`` overschrijft instellingen
uit de basis configuratie.

* ``ZAAKMAGAZIJN_GEMEENTE_CODE`` (standaard: ``0000``)

  De gemeente code die gebruikt wordt voor unieke identificatienummers.
  Haarlem is bijvoorbeeld ``0392``.

* ``ZAAKMAGAZIJN_OPEN_ACCESS`` (standaard: ``True``)

  Stelt het Zaakmagazijn open voor iedereen die verbinding kan maken. Alle
  toegangsregels worden genegeerd.

* ``ZAAKMAGAZIJN_SYSTEEM``

  Een ``dict`` die de identificatie van het Zaakmagazijn aangeeft. Kan ook een
  ``list`` van ``dict`` zijn om meerdere gemeente(code)s te ondersteunen. Kent
  de sleutels:

  - ``organisatie`` (standaard: ``ORG``)
  - ``applicatie`` (standaard: ``TTA``)
  - ``administratie`` (standaard: *(leeg)*)
  - ``gebruiker`` (standaard: *(leeg)*)

* ``ZAAKMAGAZIJN_MAX_CONTENT_LENGTH`` (standaard: ``40 * 1024 * 1024`` (40 MB))

  De maximale grootte van een XML-bestand.

* ``ZAAKMAGAZIJN_DEFAULT_MAX_NR_RESULTS`` (standaard: ``15``)

  Het standaard aantal maximum resultaten bij het opvragen van lijsten. Dit is
  de standaardwaarde in de XSD indien geen waarde wordt meegestuurd in:
  ``[...]<zkn:parameters><stuf:maximumAantal>``

* ``ZAAKMAGAZIJN_ZAAK_ID_GENERATOR``
  (standaard: ``zaakmagazijn.api.utils.create_unique_id``)

  Een functie die een uniek nummer genereert voor de service
  ``genereerZaakIdentificatie_Di02``. Er zijn 3 functies meegeleverd:

  - ``zaakmagazijn.api.utils.create_unique_id`` (standaard)

    Creeert een nummer bestaande uit de gemeente code en een UUID. Voorbeeld:
    ``039288072b1c-54f4-485c-8e83-095621e6jk24``

  - ``zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_id``

    Creeert een nummer bestaande uit het huidige jaar en een oplopend
    volgnummer binnen hetzelfde jaar. Voorbeeld: ``2017-0000001``

  - ``zaakmagazijn.contrib.idgenerator.utils.create_incremental_year_with_org_id``

    Creeert een nummer bestaande uit de ontvangende organisatie, het huidige
    jaar en een oplopend volgnummer binnen hetzelfde jaar. Voorbeeld:
    ``0392-2017-0000001``

* ``ZAAKMAGAZIJN_DOCUMENT_ID_GENERATOR``
  (standaard: ``zaakmagazijn.api.utils.create_unique_id``)

  Een functie die een uniek nummer genereert voor de service
  ``genereerDocumentIdentificatie_Du02``. Zie
  ``ZAAKMAGAZIJN_ZAAK_ID_GENERATOR`` voor mogelijke functies.

* ``ZAAKMAGAZIJN_BESLUIT_ID_GENERATOR``
  (standaard: ``zaakmagazijn.api.utils.create_unique_id``)

  Een functie die een uniek nummer genereert voor de service
  ``genereerBesluitIdentificatie_Du02``.  Zie
  ``ZAAKMAGAZIJN_ZAAK_ID_GENERATOR`` voor mogelijke functies.

* ``ZAAKMAGAZIJN_URL``

  De URL van het Zaakmagazijn waar de WSDL beschikbaar is. Voor test
  doeleinden is dit typisch ``http://localhost:8000``.

* ``ZAAKMAGAZIJN_REFERENCE_WSDL`` (standaard: ``True``)

  Gebruik de KING referentie WSDL in plaats van de gegenereerde WSDL.

* ``ZAAKMAGAZIJN_STUF_TESTPLATFORM`` (standaard: ``False``)

  Gebruik workarounds voor een installatie die gebruikt wordt voor het StUF
  test platform. Niet geschikt voor reguliere installaties!

* ``CMIS_CLIENT_URL`` (standaard: ``http://localhost:8080/alfresco/cmisatom``)

  De URL naar de DMS server.

* ``CMIS_CLIENT_USER`` (standaard: ``Admin``)

  De gebruikersnaam van de DMS gebruiker.

* ``CMIS_CLIENT_USER_PASSWORD`` (standaard: ``admin``)

  Het wachtwoord van de DMS gebruiker.

* ``CMIS_ZAKEN_TYPE_ENABLED`` (standaard: ``False``)

  Indien ``True`` geeft de hoofdfolder (eerste folder in de boomstructuur) het
  CMIS object type ``F:zsdms:zaken``. Indien ``False`` dan krijgt de
  hoofdfolder het CMIS object type ``cmis:folder``.

* ``CMIS_UPLOAD_TO`` (standaard: ``zaakmagazijn.cmis.utils.upload_to``)

  Een functie die een lijst van ``FolderConfig`` teruggeeft, om aan te geven
  waar een zaak in het DMS opgeslagen moet worden. Er zijn 2 functies
  meegeleverd:

  - ``zaakmagazijn.cmis.utils.upload_to`` (standaard)

    Boomstructuur volgens de ZDS 1.2 specificatie: ``Zaken`` >
    ``<Zaak type>`` > ``<Zaak ID>``

  - ``zaakmagazijn.cmis.utils.upload_to_date_based``

    Boomstructuur als volgt: ``Sites`` > ``archief`` > ``documentLibrary`` >
    ``<Zaak type>`` > ``<year>`` > ``<month>`` > ``<day>`` > ``<Zaak ID>``

* ``CMIS_SENDER_PROPERTY`` (standaard: ``None``)

  Zet de "stuurgegevens/zender" informatie in dit DMS veld. Laat ``None``
  indien er geen veld hiervoor in het DMS aanwezig is. Het DMS veld wordt
  gevuld met het meest specifieke zender veld in het verzoek aan het ZM.


Commando's
==========

Commando's kunnen worden uitgevoerd middels::

    $ python src/manage.py <commando>

Naast alle standaard commando's biedt het zaakmagazijn de volgende commando's:

* ``cmis_integratie [--dryrun]``

  Bedoeld als CRON-job, om met regelmatige intervallen wijzigingen in het DMS
  over te brengen in het Zaakmagazijn.

* ``overdragen_zaak <application name> <zaak ID> [-m <message>] [--dryrun]``

  Biedt de mogelijkheid om een zaak over te dragen aan een applicatie.
