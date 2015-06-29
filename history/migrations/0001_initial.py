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
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('md5', models.CharField(default=b'', max_length=32)),
                ('value', models.TextField(null=True, blank=True)),
                ('is_default', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('tool', models.CharField(max_length=50)),
                ('version', models.CharField(max_length=20)),
                ('configuration', models.TextField()),
                ('slurm_output', models.TextField()),
                ('status', models.IntegerField(max_length=1, choices=[(0, b'finished'), (1, b'finished (no output)'), (2, b'broken'), (3, b'running'), (4, b'scheduled'), (5, b'not scheduled')])),
                ('flag', models.IntegerField(default=0, max_length=1, choices=[(0, b'public'), (1, b'shared'), (2, b'private'), (3, b'deleted'), (8, b'users and guest'), (9, b'no login required')])),
                ('uid', models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column=b'uid', to_field=b'username')),
                ('version_details', models.ForeignKey(default=1, to='plugins.Version')),
            ],
            options={
                'permissions': (('history_submit_job', 'Can submit a job'), ('history_cancel_job', 'Can cancel a job'), ('browse_full_data', 'Can search all data')),
            },
        ),
        migrations.CreateModel(
            name='HistoryTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(max_length=2, choices=[(0, b'Caption'), (1, b'Public note'), (2, b'Private note'), (3, b'Deleted note'), (4, b'Follow'), (5, b'Unfollow')])),
                ('text', models.TextField()),
                ('history_id', models.ForeignKey(to='history.History')),
                ('uid', models.ForeignKey(db_column=b'uid', default=None, to_field=b'username', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('output_file', models.TextField()),
                ('preview_file', models.TextField(default=b'')),
                ('file_type', models.IntegerField(max_length=2, choices=[(0, b'data'), (1, b'plot'), (2, b'preview'), (9, b'unknown')])),
                ('history_id', models.ForeignKey(to='history.History')),
            ],
            options={
                'permissions': (('results_view_others', 'Can view results from other users'),),
            },
        ),
        migrations.CreateModel(
            name='ResultTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(max_length=2, choices=[(0, b'Caption')])),
                ('text', models.TextField()),
                ('result_id', models.ForeignKey(to='history.Result')),
            ],
        ),
        migrations.AddField(
            model_name='configuration',
            name='history_id',
            field=models.ForeignKey(related_name='history_id', to='history.History'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='parameter_id',
            field=models.ForeignKey(related_name='parameter_id', to='plugins.Parameter'),
        ),
    ]
