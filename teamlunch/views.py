from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext, loader

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

@login_required
def profile(request):
    template = loader.get_template('teamlunch/profile.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))