from django.urls import path

from . import views

urlpatterns = [
    path('all', views.all_degrees, name='all_degrees'),
    path('degreeplan', views.degree_plan),
    path('degreereqs', views.degree_reqs),
    path('coursedata', views.course_data),
    path('stored_plans', views.stored_plans)
]
