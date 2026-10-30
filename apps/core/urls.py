from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('login/', views.login_view, name='login'),
    # Passenger point of view (public): track buses, seats, live ETA.
    path('home/', views.dashboard, name='dashboard'),
    # Admin point of view (sign-in required): full fleet management.
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    # Conductor point of view (sign-in required): scanner + terminal monitor.
    path('conductor/dashboard/', views.conductor_dashboard, name='conductor_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]