from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse

from django.shortcuts import render_to_response
from formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory, BaseFormSet
from .models import TeamMember, Team, Schedule

from .forms import TeamForm1, TeamForm2, TeamForm3, TeamForm4
from allauth.account.forms import LoginForm

from collections import OrderedDict

# Create your views here.
def index(request):
    template = loader.get_template('teams/index.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

FORMS = [("register", LoginForm),
         ("coordinator", TeamForm1),
         ("teamname", TeamForm2),
         ("teammates", formset_factory(TeamForm3, extra=5)),
         ("schedule", TeamForm4)]

TEMPLATES = {"register": "teams/wizard_register.html",
             "coordinator": "teams/wizard_coordinator.html",
             "teamname": "teams/wizard_teamname.html",
             "teammates": "teams/wizard_teammates.html",
             "schedule": "teams/wizard_schedule.html"}

def show_login_step(wizard):
    # check if the field ``leave_message`` was checked.
    return not wizard.request.user.is_authenticated()

class TeamWizard(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        keys = self.get_form_list().keys()

        # Create Team
        created_team = Team(
            name = form_list[keys.index('teamname')].cleaned_data['name']
        )
        created_team.save()

        # Create TeamMember for User
        created_team_member = TeamMember(
            user = self.request.user,
            is_coordinator = True,
            team = created_team,
            display_name = form_list[keys.index('coordinator')].cleaned_data['display_name']
        )
        created_team_member.save()

        # Create Schedule
        schedule_form_data = form_list[keys.index('schedule')].cleaned_data
        created_schedule = Schedule(
            team = created_team,
            occurrence_frequency = schedule_form_data['occurrence_frequency'],
            occurrence_day_of_week = schedule_form_data['occurrence_day_of_week'],
            occurrence_day_of_month = schedule_form_data['occurrence_day_of_month'],
            advance_notification_days = schedule_form_data['advance_notification_days'],
        )
        created_schedule.save()

        # Iterate Over New TeamMembers
        created_team_mates = list()
        for team_member in form_list[keys.index('teammates')].cleaned_data:
            if team_member:
                created_team_mates.append((team_member['name'], team_member.get('email', None)))

        # Return Info to Template
        return render_to_response('teams/done.html', {
            'team' : created_team,
            'coordinator' : created_team_member,
            'mates' : created_team_mates,
            'schedule' : created_schedule
        })

    def get_form(self, step=None, data=None, files=None):
        form = super(SessionWizardView, self).get_form(step, data, files)

        # determine the step if not given
        if step is None:
            step = self.steps.current

        if step == 'coordinator':
            form.initial['display_name'] = self.request.user.username
        return form

    def get_next_step(self, step=None):
        """
        Returns the next step after the given `step`. If no more steps are
        available, None will be returned. If the `step` argument is None, the
        current step will be determined automatically.
        """
        if step is None:
            step = self.steps.current
        form_list = self.get_form_list()
        keys = list(form_list.keys())
        # Because of the way conditional dicts work, for some reason 
        # the 'keys' can lose optional steps... luckily, our first step
        # is the only optional one, so if the fir step is missing we
        # simply move along to the next.
        # Maybe a better way?
        if step in keys:
            key = keys.index(step) + 1
        else:
            key = 0
        if len(keys) > key:
            return keys[key]
        return None

    def process_step(self, form):
        # If the user did a local login, the wizard will have merely collected
        # their login details and done nothing but validate them. So, we 
        # complete the login before proceeding "Just In Case"
        if self.steps.current == 'register':
            form.login(self.request)
        return self.get_form_step_data(form)