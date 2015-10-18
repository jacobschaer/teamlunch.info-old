# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0011_auto_20151018_0503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(related_name='member_set', to='teams.Team'),
        ),
    ]
