# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='coordinator',
            field=models.ManyToManyField(to='teams.Team'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(related_name='member', to='teams.Team'),
        ),
    ]
