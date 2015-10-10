from django import forms
from django.forms import Form, ModelForm
from .models import TeamMember, Team


class TeamForm1(Form):
    coordinator_name = forms.CharField(max_length=255)

class TeamForm2(Form):
    team_name = forms.CharField(max_length=255)

class TeamForm3(ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'email']

class TeamForm4(Form):
    lunch_schedule = forms.CharField(max_length=255)
