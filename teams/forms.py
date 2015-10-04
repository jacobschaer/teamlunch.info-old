from django import forms

class TeamForm1(forms.Form):
    coordinator_name = forms.CharField(max_length=255)

class TeamForm2(forms.Form):
    team_name = forms.CharField(max_length=255)

class TeamForm3(forms.Form):
    team_member_name = forms.CharField(max_length=255)

class TeamForm4(forms.Form):
    lunch_schedule = forms.CharField(max_length=255)
