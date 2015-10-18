# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0010_lunch'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lunch',
            old_name='event_date',
            new_name='date',
        ),
        migrations.AddField(
            model_name='lunch',
            name='location',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='lunch',
            name='picker',
            field=models.ForeignKey(default=0, to='teams.TeamMember'),
            preserve_default=False,
        ),
    ]
