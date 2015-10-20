from datetime import date, timedelta
from importlib import import_module
import random

from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import signals
from django_enumfield import enum
from django.utils.translation import ugettext_lazy as _

from organizations.backends import invitation_backend
from organizations.base import (OrganizationBase, OrganizationUserBase, OrganizationOwnerBase)
from organizations.models import get_user_model

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
ORGS_SLUGFIELD = getattr(settings, 'ORGS_SLUGFIELD',
        'django_extensions.db.fields.AutoSlugField')
ORGS_TIMESTAMPED_MODEL = getattr(settings, 'ORGS_TIMESTAMPED_MODEL',
        'django_extensions.db.models.TimeStampedModel')

ERR_MSG = """You may need to install django-extensions or similar library. See
the documentation."""

try:
    module, klass = ORGS_SLUGFIELD.rsplit('.', 1)
    SlugField = getattr(import_module(module), klass)
except:
    raise ImproperlyConfigured("Your SlugField class, '{0}',"
            " is improperly defined. {1}".format(ORGS_SLUGFIELD, ERR_MSG))

try:
    module, klass = ORGS_TIMESTAMPED_MODEL.rsplit('.', 1)
    TimeStampedModel = getattr(import_module(module), klass)
except:
    raise ImproperlyConfigured("Your TimeStampedBaseModel class, '{0}',"
            " is improperly defined. {1}".format(ORGS_TIMESTAMPED_MODEL, ERR_MSG))

# Create your models here.

class Team(OrganizationBase): 
    slug = SlugField(max_length=200, blank=False, editable=True,
            populate_from='name', unique=True,
            help_text=_("The name in all lowercase, suitable for URL identification"))

    class Meta(OrganizationBase.Meta):
        verbose_name = _("team")
        verbose_name_plural = _("teams")

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'team_id': self.pk})

    def add_user(self, user, is_admin=False):
        """
        Adds a new user and if the first user makes the user an admin and
        the owner.
        """
        users_count = self.users.all().count()
        if users_count == 0:
            is_admin = True
        # TODO get specific org user?
        org_user = TeamMember.objects.create(user=user,
                organization=self, is_admin=is_admin)
        if users_count == 0:
            # TODO get specific org user?
            TeamOwner.objects.create(organization=self,
                    organization_user=org_user)

        # User added signal
        user_added.send(sender=self, user=user)
        return org_user

    def remove_user(self, user):
        """
        Deletes a user from an organization.
        """
        org_user = TeamMember.objects.get(user=user,
                                                organization=self)
        org_user.delete()

        # User removed signal
        user_removed.send(sender=self, user=user)

    def get_or_add_user(self, user, **kwargs):
        """
        Adds a new user to the organization, and if it's the first user makes
        the user an admin and the owner. Uses the `get_or_create` method to
        create or return the existing user.
        `user` should be a user instance, e.g. `auth.User`.
        Returns the same tuple as the `get_or_create` method, the
        `OrganizationUser` and a boolean value indicating whether the
        OrganizationUser was created or not.
        """
        is_admin = kwargs.pop('is_admin', False)
        users_count = self.users.all().count()
        if users_count == 0:
            is_admin = True

        org_user, created = TeamMember.objects.get_or_create(
                organization=self, user=user, defaults={'is_admin': is_admin})

        if users_count == 0:
            TeamOwner.objects.create(organization=self,
                    organization_user=org_user)

        if created:
            # User added signal
            user_added.send(sender=self, user=user)
        return org_user, created

    def change_owner(self, new_owner):
        """
        Changes ownership of an organization.
        """
        old_owner = self.owner.organization_user
        self.owner.organization_user = new_owner
        self.owner.save()

        # Owner changed signal
        owner_changed.send(sender=self, old=old_owner, new=new_owner)

    def is_admin(self, user):
        """
        Returns True is user is an admin in the organization, otherwise false
        """
        return True if self.organization_users.filter(user=user, is_admin=True) else False

    def is_owner(self, user):
        """
        Returns True is user is the organization's owner, otherwise false
        """
        return self.owner.organization_user.user == user

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
        return TeamMember.objects.create(user=user,
                organization=self,
                is_admin=admin)


class TeamMember(OrganizationUserBase):
    is_admin = models.BooleanField(default=False)

    class Meta(OrganizationUserBase.Meta):
        verbose_name = _("team member")
        verbose_name_plural = _("team members")

    def __unicode__(self):
        return u"{0} ({1})".format(self.name if self.user.is_active else
                self.user.email, self.organization.name)

    def delete(self, using=None):
        """
        If the organization user is also the owner, this should not be deleted
        unless it's part of a cascade from the Organization.
        If there is no owner then the deletion should proceed.
        """
        from organizations.exceptions import OwnershipRequired
        try:
            if self.team.owner.organization_user.id == self.id:
                raise OwnershipRequired(_("Cannot delete organization owner "
                    "before organization or transferring ownership."))
        # TODO This line presumes that OrgOwner model can't be modified
        except TeamOwner.DoesNotExist:
            pass
        super(OrganizationUserBase, self).delete(using=using)


class TeamOwner(OrganizationOwnerBase):
    class Meta:
        verbose_name = _("team owner")
        verbose_name_plural = _("team owners")

    def save(self, *args, **kwargs):
        """
        Extends the default save method by verifying that the chosen
        organization user is associated with the organization.
        Method validates against the primary key of the organization because
        when validating an inherited model it may be checking an instance of
        `Organization` against an instance of `CustomOrganization`. Mutli-table
        inheritence means the database keys will be identical though.
        """
        from organizations.exceptions import OrganizationMismatch
        if self.organization_user.organization.pk != self.organization.pk:
            raise OrganizationMismatch
        else:
            super(OrganizationOwnerBase, self).save(*args, **kwargs)


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
    picker = models.ForeignKey(TeamMember)
    location = models.CharField(max_length=255, blank=True, null=True)