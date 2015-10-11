# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0005_auto_20151011_0706'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teammember',
            old_name='name',
            new_name='display_name',
        ),
        migrations.RemoveField(
            model_name='teammember',
            name='coordinator',
        ),
        migrations.RemoveField(
            model_name='teammember',
            name='email',
        ),
        migrations.AddField(
            model_name='teammember',
            name='is_coordinator',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
