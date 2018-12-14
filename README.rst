============
Zaakmagazijn
============

:Version: 0.9.14
:Source: https://github.com/Haarlem/zaakregistratiecomponent
:Keywords: zaaksysteem, zakenmagazijn, zds, zaakservices, documentservices, soap, zds

|build-status| |coverage|


Implementatie van het referentiecomponent Zaaksysteem (ZS) volgens de
Standaard Zaak- en Documentservices (ZDS) 1.2 specificatie van KING ten
behoeve van zaakgericht werken.

Ontwikkeld door `Maykin Media B.V. <https://www.maykinmedia.nl>`_ in opdracht
van de Gemeente Haarlem.


Introductie
===========

Het Zaakmagazijn is een systeem dat invulling geeft aan de referentiecomponent
ZS en ondersteunt daarmee functionaliteit voor het opslaan en ontsluiten van
zaak- en daaraan gerelateerde statusgegevens ongeacht het zaaktype.
Vanuit dit systeem kunnen zowel interne als externe stakeholders inzicht
krijgen in de status, de bij de uitvoering betrokken partijen, de doorlooptijd
van afhandeling van zaken en daarmee ook in de kwaliteit van uitvoer van het
proces. Opslag van zaakgegevens gebeurt conform het RGBZ (2.0), het RSGB (2.0)
en het ImZTC (2.1).

Het Zaakmagazijn ondersteunt de volgende functionaliteiten:

* Aanmaken, delen en wijzigen van zaken
* Faciliteren van aanmaken, delen en wijzigen van zaakgerelateerde documenten
  (daadwerkelijke opslag vindt plaats in het DMS)
* Genereren unieke zaakidentificatienummers
* Genereren unieke documentidentificatienummers
* Synchroniseren van zaakgegevens die zijn vastgelegd in het DMS o.b.v. CMIS;

Het Zaakmagazijn biedt bovenstaande functionaliteit aan middels services. De
functionaliteit wordt niet aangeboden via een userinterface. Er is echter wel
een webinterface beschikbaar voor inzage in de ruwe data.


Opmerking
=========

De ZDS 1.2 specificatie is gebaseerd op RGBZ 1.0. In deze implementatie is
echter gebruik gemaakt van RGBZ 2.0. Middels een tussenlaag wordt een RGBZ 1.0
data model geëmuleerd.


Documentatie
============

Zie ``INSTALL.rst`` voor installatie instructies, commando's en instellingen.

* `CMIS 1.0 (Content Management Interoperability Services) <http://docs.oasis-open.org/cmis/CMIS/v1.0/os/cmis-spec-v1.0.pdf>`_ (PDF)
* `RGBZ 2.0 (Referentiemodel Gemeentelijke Basisgegevens Zaken) <http://www.gemmaonline.nl/index.php/RGBZ_2.0_in_ontwikkeling>`_
* `RSGB 3.0 (Referentiemodel Stelsel Gemeentelijke Basisgegevens) <http://www.gemmaonline.nl/index.php/RSGB_3.0_in_ontwikkeling>`_
* `StUF 3.01 (Standaard Uitwisseling Formaat) <http://gemmaonline.nl/index.php/StUF_Berichtenstandaard#StUF_3.01_familie>`_
* `Sectormodel StUF-ZKN 3.10 <http://www.gemmaonline.nl/index.php/Sectormodellen_Zaken:_StUF-ZKN>`_
* `StUF protocolbindingen 3.02 <http://www.gemmaonline.nl/images/gemmaonline/1/16/Stuf.bindingen.030200.pdf>`_ (PDF)
* `Informatiemodel Zaaktypen/Zaaktypecatalogus 2.1 (ImZTC) <http://www.gemmaonline.nl/index.php/Informatiemodel_Zaaktypen_(ImZTC)>`_
* `Keuzen VerStUFfing RGBZ <http://gemmaonline.nl/index.php/Sectormodellen_Zaken:_StUF-ZKN>`_


Verwijzingen
============

* `Community <https://discussie.kinggemeenten.nl/discussie/gemma/koppelvlak-zs-dms>`_ (rapporteren van bugs,
  functionaliteit aanvragen, algemene vragen)
* `Issues <https://github.com/maykinmedia/zaakregistratiecomponent/issues>`_
* `Code <https://github.com/maykinmedia/zaakregistratiecomponent>`_


.. |build-status| image:: https://secure.travis-ci.org/Haarlem/zaakregistratiecomponent.svg?branch=develop
    :alt: Build status
    :target: https://travis-ci.org/Haarlem/zaakregistratiecomponent

.. |coverage| image:: https://codecov.io/github/maykinmedia/zaakregistratiecomponent/coverage.svg?branch=develop
    :alt: Coverage
    :target: https://codecov.io/github/Haarlem/zaakregistratiecomponent?branch=develop
