# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hindcast_frontend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hindcastevaluation',
            name='path',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
