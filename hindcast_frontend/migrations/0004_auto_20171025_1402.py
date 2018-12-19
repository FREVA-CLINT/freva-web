# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hindcast_frontend', '0003_auto_20171025_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hindcastevaluation',
            name='path_fieldmean',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='hindcastevaluation',
            name='path_map',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
