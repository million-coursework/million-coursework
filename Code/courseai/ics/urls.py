from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path(r'', TemplateView.as_view(template_name='dynamic_pages/index.html'), name='index'),
    path(r'about/', TemplateView.as_view(template_name='dynamic_pages/about.html'), name='about'),
    path(r'planner', views.planner, name='planner'),
]
