# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_auto_20151009_0531'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('freqency', models.IntegerField(default=1)),
                ('day_of_week', models.IntegerField(default=None, blank=True)),
                ('day_of_month', models.IntegerField(blank=True)),
                ('team', models.ForeignKey(to='teams.Team')),
            ],
        ),
    ]
