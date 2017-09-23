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

  Een ``dict`` die de identificatie van het Zaakmagazijn aangeeft. Kent de
  sleutels:

  - ``organisatie`` (standaard: ``ORG``)
  - ``applicatie`` (standaard: ``TTA``)
  - ``administratie`` (standaard: *(leeg)*)
  - ``gebruiker`` (standaard: *(leeg)*)

* ``CMIS_CLIENT_URL`` (standaard: ``http://localhost:8080/alfresco/cmisatom``)

  De URL naar de DMS server.

* ``CMIS_CLIENT_USER`` (standaard: ``Admin``)

  De gebruikersnaam van de DMS gebruiker.

* ``CMIS_CLIENT_USER_PASSWORD`` (standaard: ``admin``)

  Het wachtwoord van de DMS gebruiker.


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


Ontwikkelaars
=============

Ontwikkelaars kunnen snel aan de slag door de volgende stappen te volgen:

#. Download de code in de folder waar je de applicatie wilt hebben.

#. Start en configureer de DMS:

   #. Installeer de ontwikkelomgeving middels Vagrant::

        $ cd deployment/alfresco
        $ vagrant up
        $ cd ../..

   #. Zie verder de ``README.rst`` in de ``deployment/alfresco`` folder.

#. Creeer een database en database gebruiker die toegang heeft middels een
   wachtwoord. Standaard gebruiken we als databasenaam en gebruikersnaam
   "zaakmagazijn".

#. Creeer en activeer de virtuele omgeving::

    $ virtualenv env
    $ source env/bin/activate

#. Installeer alle afhankelijkheden voor het zaakmagazijn::

    $ pip install -r requirements/dev.txt

#. Kopieer ``src/zaakmagazijn/conf/local_example.py`` naar
   ``src/zaakmagazijn/conf/local.py`` en open deze in een editor:

   #. Configureer de database backend.

   #. Configureer de DMS backend. Deze staat reeds ingesteld op de Vagrant
       configureatie.

#. Creeer de statische bestanden en de database tabellen::

    $ python src/manage.py collectstatic --link
    $ python src/manage.py migrate

#. Maak een ``superuser`` aan::

    $ python src/manage.py createsuperuser

#. Start de webserver::

    $ python src/manage.py runserver

#. Ga naar: http://localhost:8000/admin/


De WSDLs zijn nu te vinden op:

* http://localhost:8000/Beantwoordvraag/?WSDL
* http://localhost:8000/OntvangAsynchroon/?WSDL
* http://localhost:8000/VerwerkSynchroonVrijBericht/?WSDL

De beheer interface is beschikbaar op:

* http://localhost:8000/admin/


Testsuite
---------

De testsuite kan als volgt worden uitgevoerd::

    $ python src/manage.py test zaakmagazijn
