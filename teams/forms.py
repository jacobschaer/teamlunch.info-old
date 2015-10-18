from django import forms
from django.forms import Form, ModelForm
from .models import TeamMember, Team, Schedule


class TeamForm1(ModelForm):
    class Meta:
        model = TeamMember
        fields = ['display_name']

class TeamForm2(ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class TeamForm3(Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField(max_length=254)

class TeamForm4(ModelForm):
    class Meta:
        model = Schedule
        fields = ['occurrence_frequency', 'occurrence_day_of_week', 'occurrence_day_of_month', 'advance_notification_days']

class YelpForm(Form):
    location = forms.CharField(max_length=255)
    search = forms.CharField(max_length=255)