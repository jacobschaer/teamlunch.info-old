from django.conf.urls import url, include

from . import views
from .views import FORMS, show_login_step

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/', views.TeamWizard.as_view(FORMS,  
        condition_dict={'register' : show_login_step}),
        name='add'),
    url(r'^(?P<team_id>[0-9]+)/$', views.view_team, name='detail'),
    url(r'^(?P<team_id>[0-9]+)/(?P<lunch_id>[0-9]+)/edit/$', views.edit_lunch, name='edit_lunch'),
    url(r'^(?P<team_id>[0-9]+)/(?P<lunch_id>[0-9]+)/location/$', views.set_lunch_location, name='set_lunch_location'),
    url(r'^venue/$', views.venue, name='venue'),
]
