from django import forms
from django.forms import Form, ModelForm
from .models import Team, Schedule


class TeamForm2(ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class TeamForm3(Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=254)

class TeamForm4(ModelForm):
    class Meta:
        model = Schedule
        fields = ['occurrence_frequency', 'occurrence_day_of_week', 'occurrence_day_of_month', 'advance_notification_days']

class YelpForm(Form):
    location = forms.CharField(max_length=255)
    search = forms.CharField(max_length=255)