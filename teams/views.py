from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse

from django.shortcuts import render_to_response
from formtools.wizard.views import SessionWizardView
from django.forms.formsets import formset_factory
from .models import TeamMember, Team

from .forms import TeamForm1, TeamForm2, TeamForm3, TeamForm4


# Create your views here.
def index(request):
    template = loader.get_template('teams/index.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def add(request):
    template = loader.get_template('teams/add.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))


FORMS = [("username", TeamForm1),
         ("teamname", TeamForm2),
         ("teammates", formset_factory(TeamForm3, extra=2)),
         ("schedule", TeamForm4)]

TEMPLATES = {"username": "teams/wizard_username.html",
             "teamname": "teams/wizard_teamname.html",
             "teammates": "teams/wizard_teammates.html",
             "schedule": "teams/wizard_schedule.html"}

class TeamWizard(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = dict()
        for form in form_list:
            for key in form.cleaned_data.keys():
                form_data[key] = form.cleaned_data[key]
        return render_to_response('teams/done.html', {
            'form_data': form_data,
        })