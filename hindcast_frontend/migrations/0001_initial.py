# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HindcastEvaluation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=255)),
                ('score', models.CharField(max_length=50)),
                ('eva_time_start', models.IntegerField()),
                ('eva_time_end', models.IntegerField()),
                ('eva_type', models.CharField(max_length=10, choices=[(b'map', b'map'), (b'fieldmean', b'fieldmean')])),
                ('region', models.CharField(max_length=255)),
                ('time_frequency', models.CharField(max_length=255)),
                ('variable', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('hindcast_set', models.CharField(max_length=255)),
            ],
        ),
    ]
