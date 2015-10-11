# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0006_auto_20151011_0740'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='occurrence_freqency',
            new_name='occurrence_frequency',
        ),
    ]
