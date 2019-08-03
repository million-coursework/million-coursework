from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('give_feedback', views.give_feedback, name='give_feedback'),
	path('success', views.successView, name='success'),
]