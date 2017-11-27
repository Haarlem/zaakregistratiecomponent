from spyne import Unicode
from spyne.model.complex import XmlAttribute

from ...utils.stuf_datetime import IndicatieOnvolledigeDatum
from ..stuf.choices import ScopeChoices
from .constants import STUF_XML_NS, XMIME_XML_NS
from .simple_types import Entiteittype, Exact, Functie

Bestandsnaam = Unicode.customize(__namespace__=STUF_XML_NS, type_name='Bestandsnaam', max_len=255)

ContentType = Unicode.customize(__namespace__=XMIME_XML_NS, type_name='ContentType', min_len=3)

# J = de datum heeft een waarde maar jaar, maand en dag zijn onbekend
# M = de datum heeft een waarde maar maand en dag zijn onbekend
# D = de datum heeft een waarde maar de dag is onbekend
# V = datum is volledig
IndOnvolledigeDatum = Unicode.customize(__namespace__=STUF_XML_NS, type_name='IndOnvolledigeDatum', values=set(IndicatieOnvolledigeDatum.values.keys()), default='V')

NoValue = Unicode.customize(__namespace__=STUF_XML_NS, type_name='NoValue', values={'nietOndersteund', 'nietGeautoriseerd', 'geenWaarde', 'waardeOnbekend', 'vastgesteldOnbekend'})

Scope__Anonymous = Unicode.customize(__namespace__=STUF_XML_NS, values=set(ScopeChoices.values.keys()))


# T = Toevoeging
# W = Wijziging of correctie
# V = Verwijdering
# E = Een relatie entiteit wordt beeindigd.
# I = Entiteit bevat alleen identificerende gegevens.
# R = Een relatie entiteit wordt vervangen door een nieuwe relatie entiteit.
# S = De sleutel van een entiteit wordt gewijzigd.
# O = Het object in de oude entiteit wordt in het kader van een ontdubbeling samengevoegd met het object in de
#     nieuwe entiteit. Het object in de oude entiteit komt niet voor in het zendende systeem.
#     Objecten in een systeem worden veelal ontdubbeld als blijkt dat ze verwijzen naar hetzelfde object
#     in de werkelijkheid.
# Verwerkingssoort = Enum('T', 'W', 'V', 'E', 'I', 'R', 'S', 'O', type_name='Verwerkingssoort').customize(__namespace__=STUF_XML_NS, max_len=1)
Verwerkingssoort = Unicode.customize(__namespace__=STUF_XML_NS, type_name='Verwerkingssoort', max_len=1)

# StUF global attributes

indOnvolledigeDatum = XmlAttribute(IndOnvolledigeDatum, ref='indOnvolledigeDatum')

entiteittype = XmlAttribute(Entiteittype, ref='entiteittype')

# NOTE: It should just be a Boolean attribute with default=True but Spyne bugs out in that case.
exact = XmlAttribute(Exact, ref='exact')

noValue = XmlAttribute(NoValue, ref='noValue')

verwerkingssoort = XmlAttribute(Verwerkingssoort, ref='verwerkingssoort')

scope = XmlAttribute(Scope__Anonymous, ref='scope')

functie = XmlAttribute(Functie, ref='functie')


# StUF attribute groups

element = [
    ('noValue', noValue),
    ('exact', exact),
]


entiteit = [
    #       <attribute ref="StUF:sleutelVerzendend"/>
    #       <attribute ref="StUF:sleutelOntvangend"/>
    #       <attribute ref="StUF:sleutelGegevensbeheer"/>
    #       <attribute ref="StUF:sleutelSynchronisatie"/>
    ('noValue', noValue),
    ('scope', scope),
    ('verwerkingssoort', verwerkingssoort)
]

entiteitZonderSleutels = [
    ('noValue', noValue),
    ('scope', scope),
    ('verwerkingssoort', verwerkingssoort)
]

# 'aantalVoorkomens' en 'aardAantal' zijn deprecated.
relatie = [
    #       <attributeGroup ref="StUF:entiteit"/>
    #       <attribute ref="StUF:aantalVoorkomens"/>
    #       <attribute ref="StUF:aardAantal"/>
]
