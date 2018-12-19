# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hindcast_frontend', '0002_auto_20171024_1533'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hindcastevaluation',
            name='eva_type',
        ),
        migrations.RemoveField(
            model_name='hindcastevaluation',
            name='path',
        ),
        migrations.AddField(
            model_name='hindcastevaluation',
            name='path_fieldmean',
            field=models.CharField(default=None, unique=True, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hindcastevaluation',
            name='path_map',
            field=models.CharField(default=1, unique=True, max_length=255),
            preserve_default=False,
        ),
    ]
