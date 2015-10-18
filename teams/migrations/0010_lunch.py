# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0009_auto_20151017_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lunch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_date', models.DateField()),
                ('team', models.ForeignKey(to='teams.Team')),
            ],
        ),
    ]
