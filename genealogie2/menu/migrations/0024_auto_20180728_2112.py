# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-28 19:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0023_modification_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modification',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='modification',
            name='user',
        ),
        migrations.DeleteModel(
            name='Modification',
        ),
    ]