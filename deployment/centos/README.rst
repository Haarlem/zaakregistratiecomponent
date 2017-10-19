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

#. Wijzig ``vars/setup_config.sh`` met de gewenste aanpassingen::

    vi vars/setup_config.sh

#. Wijzig de overige bestanden in de ``vars`` folder om deze overeen te laten
   komen met de configuratie in ``setup_config.sh``.

#. Wijzig ``vars/settings_example.py`` en hernoem deze naar bijv.
   ``staging.py``. Dit moet overeenkomen met de ``TARGET`` (zonder ``.py`` in
   ``vars/setup_config.sh``.

#. Voer ``setup.sh`` uit.
