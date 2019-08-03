from django.urls import path

from . import views

urlpatterns = [
    path('coursesearch/', views.index),
    path('mms', views.mms_request),
    path('majors', views.all_majors),
    path('minors', views.all_minors),
    path('specs', views.all_specs),
    path('courselists', views.course_lists)
]

