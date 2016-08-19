# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plugins', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolPullRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('tool', models.CharField(max_length=50)),
                ('tagged_version', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=10, choices=[(b'waiting', b'waiting'), (b'processing', b'processing'), (b'success', b'success'), (b'failed', b'failed')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
