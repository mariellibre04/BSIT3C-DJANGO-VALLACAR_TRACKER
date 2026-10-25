"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.bus import views as bus_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('terminal/scan/', bus_views.terminal_scan_page, name='terminal_scan'),
    path('api/checkin', bus_views.terminal_checkin_api, name='terminal_checkin_api'),
    path('api/checkin/', bus_views.terminal_checkin_api),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('info/', include('apps.info.urls')),
    path('bus/', include('apps.bus.urls')),
    path('driver/', include('apps.driver.urls')),
    path('conductor/', include('apps.conductor.urls')),
    path('passengers/', include('apps.passengers.urls')),
    path('maintenance/', include('apps.maintenance.urls')),
    path('trips/', include('apps.trips.urls')),
    path('incidents/', include('apps.incidents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)