# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-28 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mothulity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.DeleteModel(
            name='Document',
        ),
    ]