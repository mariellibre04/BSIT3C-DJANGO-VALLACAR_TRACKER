from django.shortcuts import get_object_or_404
from apps.info.models import Info
from apps.bus.models import Bus
from apps.driver.models import Driver
from apps.conductor.models import Conductor
from apps.maintenance.models import MaintenanceRecord
from apps.trips.models import Trip
from apps.incidents.models import Incident

def scoped_infos(user):
    return Info.objects.filter(user=user)

def scoped_info(user, pk):
    return get_object_or_404(scoped_infos(user), pk=pk)

def scoped_buses(user):
    return Bus.objects.filter(user=user)

def scoped_bus(user, pk):
    return get_object_or_404(scoped_buses(user), pk=pk)

def scoped_drivers(user):
    return Driver.objects.filter(user=user)

def scoped_driver(user, pk):
    return get_object_or_404(scoped_drivers(user), pk=pk)

def scoped_conductors(user):
    return Conductor.objects.filter(user=user)

def scoped_conductor(user, pk):
    return get_object_or_404(scoped_conductors(user), pk=pk)

def scoped_maintenances(user):
    return MaintenanceRecord.objects.filter(user=user)

def scoped_maintenance(user, pk):
    return get_object_or_404(scoped_maintenances(user), pk=pk)

def scoped_trips(user):
    return Trip.objects.filter(user=user)

def scoped_trip(user, pk):
    return get_object_or_404(scoped_trips(user), pk=pk)

def scoped_incidents(user):
    return Incident.objects.filter(user=user)

def scoped_incident(user, pk):
    return get_object_or_404(scoped_incidents(user), pk=pk)
