# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-11 15:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rgbz', '0013_auto_20180420_1433'),
    ]

    operations = [
        migrations.RenameField(
            model_name='informatieobject',
            old_name='vertrouwlijkaanduiding',
            new_name='vertrouwelijkaanduiding',
        ),
    ]
