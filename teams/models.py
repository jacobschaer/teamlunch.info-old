from django.db import models
from django_enumfield import enum

# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, related_name="member")
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    coordinator = models.ManyToManyField(Team)

    def __str__(self):
        return self.name

class ScheduleFrequency(enum.Enum):
    DAILY = 0
    WEELY = 1
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
    freqency = enum.EnumField(ScheduleFrequency, default=ScheduleFrequency.WEELY)
    day_of_week = enum.EnumField(ScheduleDayOfWeek, default=None, blank=True)
    day_of_month = models.IntegerField(blank=True)