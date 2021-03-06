# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-08-22 21:22
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import re
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxBrainRun',
            fields=[
                ('outputs', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, null=True)),
                ('aggr_outputs', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False, unique=True)),
                ('error_text', models.CharField(blank=True, default=None, max_length=4000, null=True)),
                ('creation_date', models.DateTimeField(default=datetime.datetime(2015, 1, 1, 0, 0, tzinfo=utc))),
                ('exp_comp_datetime', models.DateTimeField(default=datetime.datetime(2015, 1, 1, 0, 0, tzinfo=utc))),
                ('job_id', models.UUIDField(blank=True, default=None, null=True)),
                ('upstream_vers', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('webapp_vers', models.CharField(blank=True, default=None, max_length=50, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaxSaveInputs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_gui_field_inputs', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, null=True)),
                ('gui_field_inputs', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, null=True)),
                ('inputs_file', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('errors_warnings_text', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, null=True)),
                ('upstream_parameters', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('first_year', models.IntegerField(default=None, null=True)),
                ('years_n', models.CharField(max_length=300, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z', 32), code='invalid', message='Enter only digits separated by commas.')])),
                ('data_source', models.CharField(blank=True, default='PUF', max_length=20, null=True)),
                ('quick_calc', models.BooleanField(default=False)),
                ('deprecated_fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), blank=True, null=True, size=None)),
            ],
            options={
                'permissions': (('view_inputs', 'Allowed to view Taxbrain.'),),
            },
        ),
        migrations.AddField(
            model_name='taxbrainrun',
            name='inputs',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='outputs', to='taxbrain.TaxSaveInputs'),
        ),
        migrations.AddField(
            model_name='taxbrainrun',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
