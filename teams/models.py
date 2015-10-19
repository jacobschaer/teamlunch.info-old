from datetime import date, timedelta
import random
from django.core.mail import send_mail

from django.conf import settings
from django.db import models
from django_enumfield import enum
from django.db.models import signals
from organizations.models import Organization, OrganizationUser, get_user_model
from organizations.backends import invitation_backend

# Create your models here.

class Team(Organization):   
    def choose_member(self):
        return random.choice(self.organization_users.all())

    def notify_members(self):
        message1 = ('Subject here', 'Here is the message', 'from@example.com', ['first@example.com', 'other@example.com'])
        message2 = ('Another Subject', 'Here is another message', 'from@example.com', ['second@test.com'])
        send_mass_mail((message1, message2), fail_silently=False)

    def get_teammember(self, user):
        for team_member in self.users.all():
            if team_member == user:
                return team_member

    def get_current_lunch(self):
        try:
            return self.lunch_set.latest(field_name='date')
        except Lunch.DoesNotExist:
            return None

    def invite_user(self, site, sender, first_name, last_name, email, admin=False):
        try:
            user = get_user_model().objects.get(email__iexact=email)
        except get_user_model().MultipleObjectsReturned:
            raise forms.ValidationError(_("This email address has been used multiple times."))
        except get_user_model().DoesNotExist:
            user = invitation_backend().invite_by_email(
                    email,
                    **{'domain': site,
                        'organization': self,
                        'sender': sender})
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        return OrganizationUser.objects.create(user=user,
                organization=self,
                is_admin=admin)


    def __str__(self):
        return self.name

class ScheduleFrequency(enum.Enum):
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2

class ScheduleDayOfWeek(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

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

    def should_pick_on_date(self, date):
        # Regardless of "advance_notification_days", dailies always match - it's just question
        # of what occurrence you're choosing for
        if self.occurrence_frequency == ScheduleFrequency.DAILY:
            return True
        elif self.occurrence_frequency == ScheduleFrequency.WEEKLY:
            return (self.occurrence_day_of_week - self.advance_notification_days) % 7 == date.weekday()
        elif self.occurrence_frequency == ScheduleFrequency.MONTHLY:
            return (date + timedelta(days=self.advance_notification_days)).day == self.occurrence_day_of_month

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

class Lunch(models.Model):
    team = models.ForeignKey(Team)
    date = models.DateField(auto_now=False, auto_now_add=False)
    picker = models.ForeignKey(OrganizationUser)
    location = models.CharField(max_length=255, blank=True, null=True)