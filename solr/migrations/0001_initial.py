# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCrawl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=10, choices=[(b'waiting', b'waiting'), (b'crawling', b'crawling'), (b'ingesting', b'ingesting'), (b'success', b'success'), (b'failed', b'failed')])),
                ('path_to_crawl', models.CharField(max_length=1000)),
                ('tar_file', models.CharField(max_length=255, blank=True)),
                ('ingest_msg', models.TextField(blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'solr_usercrawl',
            },
        ),
    ]
