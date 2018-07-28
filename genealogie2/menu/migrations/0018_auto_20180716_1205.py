# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-16 10:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0017_individual_is_deceased'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationship',
            name='parent1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='person1', to='menu.Individual'),
        ),
        migrations.AlterField(
            model_name='relationship',
            name='parent2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='person2', to='menu.Individual'),
        ),
    ]