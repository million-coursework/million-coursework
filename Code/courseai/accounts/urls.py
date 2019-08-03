from . import views
from django.urls import path
from django.conf.urls import include, url

urlpatterns = [
    path('login_view', views.login_view, name='login'),
    path('register_view', views.register_view, name='register'),
    path('logout_view', views.logout_view, name='logout'),
    path('degree_plan_view', views.code_view),
    path('profile', views.get_user_profile, name="profile"),
    # path('account_activate_view', views.account_activate_view, name='activate')
]
