from django.conf.urls import url

from . import views
from .views import FORMS

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/', views.TeamWizard.as_view(FORMS), name='add')
]
