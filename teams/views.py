from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse

from django.shortcuts import render_to_response
from formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory, BaseFormSet
from .models import TeamMember, Team

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
        form_data = dict()
        for form in form_list:
            current_data = form.cleaned_data
            if type(current_data) == list:
                for sub_form in current_data:
                    for key in sub_form.keys():
                        if not key in form_data:
                            form_data[key] = list()
                        form_data[key].append(sub_form[key])
            else:
                for key in form.cleaned_data.keys():
                    form_data[key] = form.cleaned_data[key]
        return render_to_response('teams/done.html', {
            'form_data': form_data,
        })

    def get_form(self, step=None, data=None, files=None):
        form = super(SessionWizardView, self).get_form(step, data, files)

        # determine the step if not given
        if step is None:
            step = self.steps.current

        if step == 'coordinator':
            form.initial['coordinator_name'] = self.request.user.username
        return form
