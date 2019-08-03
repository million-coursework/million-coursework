"""courseai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import include, url
from django.views.generic import TemplateView
from .admin import site


urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + [
    path(r'', include('ics.urls')),
    path(r'search/', include('search.urls')),
    path(r'degree/', include('degree.urls')),
    path(r'accounts/', include('accounts.urls')),
    path(r'recommendations/', include('recommendations.urls')),
    path(r'admin/', site.urls),
    path(r'feedback/', include('feedback.urls')),
    path(r'feedbackform', TemplateView.as_view(template_name='dynamic_pages/feedback.html'), name='feedbackform')
]
