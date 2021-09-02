# Generated by Django 3.2.2 on 2021-05-20 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HindcastEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path_map', models.CharField(blank=True, max_length=255, null=True)),
                ('path_fieldmean', models.CharField(blank=True, max_length=255, null=True)),
                ('score', models.CharField(max_length=50)),
                ('eva_time_start', models.IntegerField()),
                ('eva_time_end', models.IntegerField()),
                ('region', models.CharField(max_length=255)),
                ('time_frequency', models.CharField(max_length=255)),
                ('variable', models.CharField(max_length=255)),
                ('reference', models.CharField(max_length=255)),
                ('hindcast_set', models.CharField(max_length=255)),
            ],
        ),
    ]