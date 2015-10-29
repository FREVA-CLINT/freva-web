# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('externaluser', '0002_auto_20150914_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externaluser',
            name='status',
            field=model_utils.fields.StatusField(default=b'pending', max_length=100, verbose_name='status', no_check_for_status=True, choices=[(0, 'dummy')]),
        ),
    ]
