from django.urls import path
from . import views

app_name = 'bus'

urlpatterns = [
    path('', views.bus_list_page, name='bus_list'),
    path('map/', views.bus_map_page, name='bus_map'),
    path('kiosk/', views.bus_kiosk_page, name='bus_kiosk'),
    path('tap/<uuid:token>/', views.bus_tap_page, name='bus_tap'),
    path('eta/', views.passenger_eta_page, name='passenger_eta'),
    path('ajax/list/', views.bus_list_ajax, name='bus_list_ajax'),
    path('ajax/locations/', views.bus_locations_ajax, name='bus_locations_ajax'),
    path('ajax/geocode/', views.geocode_ajax, name='geocode_ajax'),
    path('ajax/get/<int:pk>/', views.bus_get_ajax, name='bus_get_ajax'),
    path('ajax/save/', views.bus_save_ajax, name='bus_save_ajax'),
    path('ajax/gps/<int:pk>/', views.bus_gps_update_ajax, name='bus_gps_update_ajax'),
    path('ajax/delete/<int:pk>/', views.bus_delete_ajax, name='bus_delete_ajax'),
]
