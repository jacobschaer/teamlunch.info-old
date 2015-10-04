from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse

from django.shortcuts import render_to_response
from formtools.wizard.views import SessionWizardView

# Create your views here.
def index(request):
    template = loader.get_template('teams/index.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

def add(request):
    template = loader.get_template('teams/add.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

class TeamWizard(SessionWizardView):
    def get_template_names(self):
        return 'teams/team_wizard.html'

    def done(self, form_list, **kwargs):
        form_data = dict()
        for form in form_list:
            for key in form.cleaned_data.keys():
                form_data[key] = form.cleaned_data[key]
        return render_to_response('teams/done.html', {
            'form_data': form_data,
        })