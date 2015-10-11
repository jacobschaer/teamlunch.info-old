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
    occurrence_frequency = enum.EnumField(ScheduleFrequency, default=ScheduleFrequency.WEEKLY)
    occurrence_day_of_week = enum.EnumField(ScheduleDayOfWeek, default=ScheduleDayOfWeek.FRIDAY, blank=True, null=True)
    occurrence_day_of_month = models.IntegerField(blank=True, null=True)
    advance_notification_days = models.IntegerField(default=1)

    def order_string(self, number):
        suffix = {
            1 : 'st',
            2 : 'nd',
            3 : 'rd',
        }

        return '{number}{suffix}'.format(number = number, suffix = suffix.get(number % 10, 'th'))


    def __str__(self):
        frequency = ''
        if self.occurrence_frequency == ScheduleFrequency.DAILY:
            frequency = 'day'
        elif self.occurrence_frequency == ScheduleFrequency.WEEKLY:
            frequency = 'week on ' + str(ScheduleDayOfWeek.values[self.occurrence_day_of_week])
        else:
            frequency = 'month on the ' + self.order_string(self.occurrence_day_of_month)
        
        return 'Lunches are scheduled every {frequency}, with someone being selected {notification} {day} in advance.'.format(
            frequency = frequency,
            notification = self.advance_notification_days,
            day = 'day' if self.advance_notification_days == 1 else 'days'
        )