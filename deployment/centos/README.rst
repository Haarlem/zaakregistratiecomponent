============================
Installatie op CentOS/RHEL 7
============================

Een eenvoudig installatie script is aanwezig om een CentOS/RHEL 7 server voor
te bereiden en het Zaakmagazijn te installeren.

Instructies
===========

Om het Zaakmagazijn te installeren, zijn de volgende stappen nodig:

#. Installeer CentOS/RHEL 7.

#. Login als ``root``.

#. Download de de installatie bestanden uit de folder ``deployment/centos`` en
   zet deze in een folder op de server, bijv. in ``zs_setup``.

#. Ga naar de folder en geef uitvoer rechten aan het setup bestand::

    cd zs_setup
    chmod +x *.sh

#. Wijzig ``vars/setup_config.sh`` met de gewenste aanpassingen::

    vi vars/setup_config.sh

#. Maak een kopie van ``vars/settings_example.py`` naar bijv. ``staging.py``.
   Dit moet overeenkomen met de ``TARGET`` (zonder ``.py``) in
   ``vars/setup_config.sh``.

   Wijzig de database, cache, cmis, zaakmagazijn en andere instellingen in
   ``staging.py``. Meer informatie staat op:

    * **Django instellingen**
      Zie: https://docs.djangoproject.com/en/1.11/ref/settings/

    * **Zaakmagazijn instellingen**
      Zie: ``INSTALL.rst``

#. Wijzig de volgende bestanden in de ``vars`` folder om deze overeen te laten
   komen met de configuratie in ``setup_config.sh``:

    * nginx.conf
    * supervisor.ini

#. Voer ``setup.sh`` uit. Er worden tijdens de installatie verschillende
   vragen gesteld::

    ./setup.sh

#. Klaar!


De WSDLs zijn nu te vinden op:

* http://<host>/BeantwoordVraag/?WSDL
* http://<host>/OntvangAsynchroon/?WSDL
* http://<host>/VerwerkSynchroonVrijBericht/?WSDL

De beheer interface is beschikbaar op:

* http://<host>/admin/


Vragen en antwoorden
====================

* Als ik naar de URL van het Zakenmagazijn ga, krijg ik ``Bad Request (400)``
  te zien.

  Controleer de log bestanden in de ``log`` folder waar het zaakmagazijn in is
  geïnstalleerd. Een veelvoorkomend probleem is dat niet de juiste domeinnaam
  of het IP van de server is toegevoegd aan ``ALLOWED_HOSTS`` in
  ``src/zaakmagazijn/conf/<settings>.py``

* Alles lijkt goed geïnstalleerd maar ik kan niet bij de URL van het
  Zakenmagazijn.

  Het kan zijn dat de beveiligingsinstellingen (SELinux) verkeerd staan.
  Hierdoor kan Nginx niet communiceren met de buitenwereld of met uWSGI. Voer
  het volgende uit::

    sudo cat /var/log/audit/audit.log | grep nginx | grep denied | audit2allow -M mynginx
    sudo semodule -i mynginx.pp

