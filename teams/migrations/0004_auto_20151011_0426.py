# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0003_schedule'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='day_of_month',
            new_name='occurrence_day_of_month',
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='day_of_week',
            new_name='occurrence_day_of_week',
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='freqency',
            new_name='occurrence_freqency',
        ),
        migrations.AddField(
            model_name='schedule',
            name='advance_notification_days',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
