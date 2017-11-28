# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-23 11:11
from __future__ import unicode_literals

from django.db import migrations, models
import zaakmagazijn.utils.fields
import zaakmagazijn.utils.stuf_datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rsgb', '0001_initial'),
        ('rgbz', '0009_delete_naam')
    ]

    operations = [
        migrations.DeleteModel(
            name='BasisAdres',
        ),
        migrations.DeleteModel(
            name='Voorvoegsel',
        ),
        migrations.RemoveField(
            model_name='adres',
            name='identificatie',
        ),
        migrations.AddField(
            model_name='adres',
            name='postcode',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='academischetitel',
            name='datum_begin_geldigheid_titel',
            field=zaakmagazijn.utils.fields.StUFDateField(default=zaakmagazijn.utils.stuf_datetime.today, help_text='De datum waarop de ACADEMISCHE TITEL is ontstaan.', max_length=9),
        ),
        migrations.AlterField(
            model_name='adresseerbaarobjectaanduiding',
            name='datum_begin_geldigheid_adresseerbaar_object_aanduiding',
            field=zaakmagazijn.utils.fields.StUFDateField(default=zaakmagazijn.utils.stuf_datetime.today, max_length=9),
        ),
        migrations.AlterField(
            model_name='openbareruimte',
            name='datum_begin_geldigheid_openbare_ruimte',
            field=zaakmagazijn.utils.fields.StUFDateField(default=zaakmagazijn.utils.stuf_datetime.today, max_length=9),
        ),
        migrations.AlterField(
            model_name='woonplaats',
            name='datum_begin_geldigheid_woonplaats',
            field=zaakmagazijn.utils.fields.StUFDateField(default=zaakmagazijn.utils.stuf_datetime.today, max_length=9),
        ),
        migrations.AlterField(
            model_name='woonplaats',
            name='datum_einde_geldigheid_woonplaats',
            field=zaakmagazijn.utils.fields.StUFDateField(blank=True, max_length=9, null=True),
        ),
    ]