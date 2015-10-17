# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0008_auto_20151011_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='occurrence_day_of_week',
            field=models.IntegerField(default=4, null=True, blank=True),
        ),
    ]
