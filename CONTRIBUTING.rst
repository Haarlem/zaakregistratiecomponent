============
Contributing
============

Graag zien we goed geteste Pull Requests tegemoet om issues te verhelpen of
nieuwe features toe te voegen.

Ontwikkelaars
=============

Ontwikkelaars die bekend zijn met Django kunnen snel aan de slag door de
volgende stappen te volgen:

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

#. Klaar!


De WSDLs zijn nu te vinden op:

* http://localhost:8000/BeantwoordVraag/?WSDL
* http://localhost:8000/OntvangAsynchroon/?WSDL
* http://localhost:8000/VerwerkSynchroonVrijBericht/?WSDL

De beheer interface is beschikbaar op:

* http://localhost:8000/admin/


Testsuite
---------

De testsuite kan als volgt worden uitgevoerd::

    $ python src/manage.py test zaakmagazijn
