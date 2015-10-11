# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0004_auto_20151011_0426'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='user',
            field=models.OneToOneField(default=0, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='schedule',
            name='advance_notification_days',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='occurrence_day_of_week',
            field=models.IntegerField(default=5, blank=True),
        ),
    ]
