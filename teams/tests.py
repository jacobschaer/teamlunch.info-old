from django.test import TestCase, Client, SimpleTestCase
from allauth.utils import get_user_model

def create_user_and_login(client):
    user = get_user_model().objects.create(username='john', is_active=True)
    user.set_password('doe')
    user.save()
    client.login(username='john', password='doe')
    return user

# Create your tests here.
class HomePageTestCase(SimpleTestCase):
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

class ProfilePageTestCase(SimpleTestCase):
    def setUp(self):
        self.c = Client()

    def test_redirect_to_login_when_not_authenticated(self):
        response = self.c.get('/accounts/profile')
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile', status_code=302, target_status_code=200)

class WizardTestCase(SimpleTestCase):
    def setUp(self):
        self.c = Client()
