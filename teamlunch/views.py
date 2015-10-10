from django.shortcuts import render, redirect
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

def profile(request):
    template = loader.get_template('teamlunch/profile.html')
    context = RequestContext(request, {})
    if request.user.id:
        return HttpResponse(template.render(context))
    else:
        return redirect('/accounts/login')