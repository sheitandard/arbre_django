# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-29 17:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0012_auto_20180628_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='city_today',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='country_today',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='country',
            field=models.CharField(max_length=40),
        ),
    ]