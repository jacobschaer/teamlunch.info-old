from django import forms
from django.forms import Form, ModelForm
from .models import TeamMember, Team, Schedule


class TeamForm1(Form):
    coordinator_name = forms.CharField(max_length=255)

class TeamForm2(Form):
    team_name = forms.CharField(max_length=255)

class TeamForm3(ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'email']

class TeamForm4(ModelForm):
    class Meta:
        model = Schedule
        fields = ['freqency', 'day_of_week', 'day_of_month']
