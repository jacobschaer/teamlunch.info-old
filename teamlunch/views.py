from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse

# Create your views here.
def index(request):
    template = loader.get_template('teamlunch/index.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

# Create your views here.
def about(request):
    template = loader.get_template('teamlunch/about.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))