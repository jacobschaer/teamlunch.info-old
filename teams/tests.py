import re
from django.core import mail
from django.test import TestCase, Client
from datetime import date
from allauth.utils import get_user_model
from .models import *
from .views import create_team
from django.core.urlresolvers import reverse

def create_user_and_login(client):
    user = get_user_model().objects.create(username='john', is_active=True)
    user.set_password('doe')
    user.save()
    client.login(username='john', password='doe')
    return user

# Create your tests here.
class HomePageTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    def test_home_page_available(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_log_in_button_present_when_not_authenticated(self):
        response = self.c.get('/')
        self.assertContains(response, 'Log In')

    def test_profile_button_present_when_authenticated(self):
        user = create_user_and_login(self.c)
        response = self.c.get('/')       
        self.assertContains(response, 'Profile')
        user.delete()

    def test_logout_button_present_when_authenticated(self):
        user = create_user_and_login(self.c)
        response = self.c.get('/')
        self.assertContains(response, 'Logout')
        user.delete()


class ProfilePageTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    def test_redirect_to_login_when_not_authenticated(self):
        response = self.c.get('/accounts/profile')
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile', status_code=302, target_status_code=200)


class WizardTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.wizard_url = reverse('teams:add')

    def test_wizard_available(self):
        response = self.c.get(self.wizard_url)
        self.assertEqual(response.status_code, 200)

    def test_first_page_is_login_if_not_already(self):
        response = self.c.get(self.wizard_url)
        self.assertEqual(response.context['wizard']['steps'].current, 'register')

    def test_register_view(self):
        user = get_user_model().objects.create(username='john', is_active=True)
        user.set_password('doe')
        user.save()
        post_data = {
          'team_wizard-current_step': ['register'],
          'register-login': ['john'],
          'register-password': ['doe']}
        response = self.c.get(self.wizard_url)
        response = self.c.post(self.wizard_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'teamname')       
        user.delete()

    def test_first_page_is_teamname_if_logged_in(self):
        user = create_user_and_login(self.c)
        response = self.c.get(self.wizard_url)
        self.assertEqual(response.context['wizard']['steps'].current, 'teamname')
        user.delete()


class InvitationTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.owner = get_user_model().objects.create(username='johnny', is_active=True)
        self.team = create_team(self.owner, 'team_amazing')
        self.created_team_member = self.team.invite_user(1, self.owner,
                                                            'jane', 'doe',
                                                            'jane_doe@example.com')
        self.created_team_member.save()

    def tearDown(self):
        self.created_team_member.delete()
        self.owner.delete()
        self.team.delete()

    def test_that_email_is_sent(self):
        self.assertEqual(mail.outbox[0].to[0], 'jane_doe@example.com')    

    def test_that_email_link_works_for_new_users(self):
        email = mail.outbox[0]
        link_regex = re.compile(r'/invitations/[^/]+/')
        invite_link = link_regex.search(email.body).group()
        response = self.c.get(invite_link)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['first_name'].value(), 'jane')
        self.assertEqual(response.context['form']['last_name'].value(), 'doe')
        self.assertEqual(response.context['form']['email'].value(), 'jane_doe@example.com')

    def test_that_email_link_works_for_existing_users(self):
        email = mail.outbox[0]
        link_regex = re.compile(r'/invitations/[^/]+/')
        invite_link = link_regex.search(email.body).group()
        existing_user = create_user_and_login(self.c)
        response = self.c.get(invite_link)
        self.assertRedirects(response, reverse('teams:detail', kwargs={'team_id' : self.team.pk}),
                             status_code=302, target_status_code=200)
        self.assertTrue(existing_user in self.team.users.all())


class ScheduleTestCase(TestCase):
    def setUp(self):
        self.sut = Schedule()

    def test_string_representation_for_days_of_month(self):
        self.assertEqual(self.sut.order_string(31), '31st')
        self.assertEqual(self.sut.order_string(29), '29th')
        self.assertEqual(self.sut.order_string(28), '28th')
        self.assertEqual(self.sut.order_string(1), '1st')
        self.assertEqual(self.sut.order_string(2), '2nd')
        self.assertEqual(self.sut.order_string(3), '3rd')

    def test_string_representation_for_daily_singular(self):
        self.sut.occurrence_frequency = ScheduleFrequency.DAILY
        self.sut.advance_notification_days = 1
        self.assertEqual(str(self.sut), 'Lunches are scheduled every day, with someone being selected 1 day in advance.')

    def test_string_representation_for_daily_plural(self):
        self.sut.occurrence_frequency = ScheduleFrequency.DAILY
        self.sut.advance_notification_days = 2
        self.assertEqual(str(self.sut), 'Lunches are scheduled every day, with someone being selected 2 days in advance.')

    def test_string_representation_for_weekly(self):
        self.sut.occurrence_frequency = ScheduleFrequency.WEEKLY
        self.sut.occurrence_day_of_week = ScheduleDayOfWeek.FRIDAY
        self.sut.advance_notification_days = 1
        self.assertEqual(str(self.sut), 'Lunches are scheduled every week on FRIDAY, with someone being selected 1 day in advance.')

    def test_string_representation_for_monthly(self):
        self.sut.occurrence_frequency = ScheduleFrequency.MONTHLY
        self.sut.occurrence_day_of_month = 2
        self.sut.advance_notification_days = 1
        self.assertEqual(str(self.sut), 'Lunches are scheduled every month on the 2nd, with someone being selected 1 day in advance.')

    def test_daily_should_pick_on_date(self):
        self.sut.occurrence_frequency = ScheduleFrequency.DAILY
        test_date = date(2015, 1, 3)
        self.assertTrue(self.sut.should_pick_on_date(test_date))

    def test_weekly_should_pick_on_date(self):
        self.sut.occurrence_frequency = ScheduleFrequency.WEEKLY
        self.sut.occurrence_day_of_week = ScheduleDayOfWeek.TUESDAY
        self.sut.advance_notification_days = 3
        test_date = date(2015, 1, 3) # Saturday
        self.assertTrue(self.sut.should_pick_on_date(test_date))
    
    def test_weekly_should_not_pick_on_date(self):
        self.sut.occurrence_frequency = ScheduleFrequency.WEEKLY
        self.sut.occurrence_day_of_week = ScheduleDayOfWeek.TUESDAY
        self.sut.advance_notification_days = 4
        test_date = date(2015, 1, 3) # Saturday
        self.assertFalse(self.sut.should_pick_on_date(test_date))

    def test_monthly_should_pick_on_date(self):
        self.sut.occurrence_frequency = ScheduleFrequency.MONTHLY
        self.sut.occurrence_day_of_month = 30
        self.sut.advance_notification_days = 4
        test_date = date(2015, 1, 26) # Saturday
        self.assertTrue(self.sut.should_pick_on_date(test_date))

    def test_monthly_should_not_pick_on_date(self):
        self.sut.occurrence_frequency = ScheduleFrequency.MONTHLY
        self.sut.occurrence_day_of_month = 30
        self.sut.advance_notification_days = 4
        test_date = date(2015, 1, 27) # Saturday
        self.assertFalse(self.sut.should_pick_on_date(test_date))

class TeamTestCase(TestCase):
    def test_one_remaining_picker(self):
        owner = get_user_model().objects.create(username='johnny', is_active=True, password='asdf')
        team = create_team(owner, 'team_amazing1')
        user1 = get_user_model().objects.create(username='a', email="a@example.com", password="asdf")
        user2 = get_user_model().objects.create(username='b', email="sexample.com", password="asdf")
        user3 = get_user_model().objects.create(username='c', email="d@example.com", password="asdf")
        member1 = team.add_user(user1)
        member2 = team.add_user(user2)
        member3 = team.add_user(user3)
        team.owner.organization_user.previously_chosen = True
        member1.previously_chosen = True
        member2.previously_chosen = True
        member1.save()
        member2.save()
        team.owner.organization_user.save()
        for i in range(0,100):
            self.assertEqual(team.choose_member(), member3)

    def test_all_remaining_pickers(self):
        owner = get_user_model().objects.create(username='johnny5', is_active=True, password='asdf')
        team = create_team(owner, 'team_amazing2')
        user1 = get_user_model().objects.create(username='d', email="f@example.com", password="asdf")
        user2 = get_user_model().objects.create(username='e', email="df@example.com", password="asdf")
        user3 = get_user_model().objects.create(username='f', email="sdf@example.com", password="asdf")
        user1.save()
        user2.save()
        user3.save()
        member1 = team.add_user(user1)
        member2 = team.add_user(user2)
        member3 = team.add_user(user3)
        for i in range(0,100):
            self.assertTrue(team.choose_member() in [team.owner.organization_user, member1, member2, member3])

    def test_no_remaining_pickers(self):
        owner = get_user_model().objects.create(username='johnny', is_active=True, password='asdf')
        team = create_team(owner, 'team_amazing1')
        user1 = get_user_model().objects.create(username='a', email="a@example.com", password="asdf")
        user2 = get_user_model().objects.create(username='b', email="sexample.com", password="asdf")
        user3 = get_user_model().objects.create(username='c', email="d@example.com", password="asdf")
        member1 = team.add_user(user1)
        member2 = team.add_user(user2)
        member3 = team.add_user(user3)
        team.owner.organization_user.previously_chosen = True
        member1.previously_chosen = True
        member2.previously_chosen = True
        member3.previously_chosen = True
        member1.save()
        member2.save()
        member3.save()
        team.owner.organization_user.save()
        team.choose_member()
        for member in team.organization_users.all():
            self.assertEqual(member.previously_chosen , False)
