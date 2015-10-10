from django.conf.urls import url, include

from . import views
from .views import FORMS, show_login_step

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/', views.TeamWizard.as_view(FORMS,  
        condition_dict={'register' : show_login_step}), name='add'),
]
