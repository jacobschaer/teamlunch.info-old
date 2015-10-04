from django.conf.urls import url
from .forms import TeamForm1, TeamForm2, TeamForm3, TeamForm4

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/', views.TeamWizard.as_view([TeamForm1, TeamForm2, TeamForm3, TeamForm4]), name='add')
]
