# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [(b'hindcast_frontend', '0001_initial'), (b'hindcast_frontend', '0002_auto_20171024_1533'), (b'hindcast_frontend', '0003_auto_20171025_1358'), (b'hindcast_frontend', '0004_auto_20171025_1402')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HindcastEvaluation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.CharField(max_length=50)),
                ('eva_time_start', models.IntegerField()),
                ('eva_time_end', models.IntegerField()),
                ('region', models.CharField(max_length=255)),
                ('time_frequency', models.CharField(max_length=255)),
                ('variable', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('hindcast_set', models.CharField(max_length=255)),
                ('path_fieldmean', models.CharField(max_length=255, null=True, blank=True)),
                ('path_map', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
    ]
