# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parameter_name', models.CharField(max_length=50)),
                ('parameter_type', models.CharField(max_length=50)),
                ('tool', models.CharField(max_length=50)),
                ('version', models.IntegerField(max_length=4)),
                ('mandatory', models.BooleanField()),
                ('default', models.CharField(max_length=255, null=True, blank=True)),
                ('impact', models.IntegerField(default=0, max_length=1, choices=[(0, b'Parameter affects values'), (5, b'Parameter affects plots'), (9, b'No effects on output')])),
            ],
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('tool', models.CharField(max_length=50)),
                ('version', models.CharField(max_length=20)),
                ('internal_version_tool', models.CharField(max_length=40)),
                ('internal_version_api', models.CharField(max_length=40)),
                ('repository', models.TextField()),
            ],
        ),
    ]
