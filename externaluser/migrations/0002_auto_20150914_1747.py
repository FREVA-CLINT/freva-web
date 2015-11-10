# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('externaluser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externaluser',
            name='email',
            field=models.EmailField(unique=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='externaluser',
            name='username',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
