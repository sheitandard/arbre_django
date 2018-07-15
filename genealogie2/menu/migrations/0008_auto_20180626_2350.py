# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-26 21:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0007_auto_20180625_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='date_of_birth',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='date_of_death',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='gender',
            field=models.CharField(blank=True, choices=[('F', 'femme'), ('M', 'homme'), ('A', 'autre')], max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='relationship',
            name='date_of_divorce',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='relationship',
            name='date_of_marriage',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]