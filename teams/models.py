from django.conf import settings
from django.db import models
from django_enumfield import enum
from django.db.models import signals

# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, related_name="member")
    display_name = models.CharField(max_length=255)
    is_coordinator = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.display_name

class ScheduleFrequency(enum.Enum):
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2

class ScheduleDayOfWeek(enum.Enum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

class Schedule(models.Model):
    team = models.ForeignKey(Team)
    occurrence_freqency = enum.EnumField(ScheduleFrequency, default=ScheduleFrequency.WEEKLY)
    occurrence_day_of_week = enum.EnumField(ScheduleDayOfWeek, default=ScheduleDayOfWeek.FRIDAY, blank=True)
    occurrence_day_of_month = models.IntegerField(blank=True)
    advance_notification_days = models.IntegerField(default=1)