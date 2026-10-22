import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.scoping import (
    scoped_buses, scoped_incidents, scoped_maintenances,
    scoped_trip, scoped_trips,
)
from apps.bus.models import Bus
from apps.incidents.models import Incident
from apps.maintenance.models import MaintenanceRecord
from .models import Trip


def _parse_dt(raw):
    raw = (raw or '').strip()
    if not raw:
        return None
    # datetime-local input: 2026-10-16T14:30
    for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
        try:
            naive = datetime.strptime(raw, fmt)
            return timezone.make_aware(naive) if timezone.is_naive(naive) else naive
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


@login_required(login_url='login')
def trip_list_page(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    trips = scoped_trips(request.user).select_related('bus').order_by('-scheduled_departure')
    if query:
        trips = trips.filter(
            Q(origin__icontains=query) | Q(destination__icontains=query)
            | Q(route__icontains=query) | Q(bus__bus_number__icontains=query)
        )
    if status_filter in dict(Trip.STATUS_CHOICES):
        trips = trips.filter(status=status_filter)
    paginator = Paginator(trips, 10)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'trips/list.html', {
        'trips': page, 'query': query, 'status_filter': status_filter,
        'status_choices': Trip.STATUS_CHOICES,
        'available_buses': scoped_buses(request.user).filter(status=Bus.STATUS_ACTIVE).order_by('bus_number'),
    })


@login_required(login_url='login')
def trip_get_ajax(request, pk):
    t = scoped_trip(request.user, pk)
    fmt = lambda v: timezone.localtime(v).strftime('%Y-%m-%dT%H:%M') if v else ''
    return JsonResponse({
        'id': t.id, 'bus_id': t.bus_id, 'origin': t.origin, 'destination': t.destination,
        'route': t.route, 'scheduled_departure': fmt(t.scheduled_departure),
        'scheduled_arrival': fmt(t.scheduled_arrival),
        'actual_departure': fmt(t.actual_departure), 'actual_arrival': fmt(t.actual_arrival),
        'status': t.status, 'delay_minutes': t.delay_minutes,
        'passenger_count': t.passenger_count, 'notes': t.notes,
    })


@login_required(login_url='login')
@require_POST
def trip_save_ajax(request):
    tid = request.POST.get('id')
    trip = scoped_trip(request.user, tid) if tid else Trip()
    is_update = bool(tid)

    bus_id = request.POST.get('bus', '').strip()
    origin = request.POST.get('origin', '').strip()
    destination = request.POST.get('destination', '').strip()
    route = request.POST.get('route', '').strip()
    s_dep = _parse_dt(request.POST.get('scheduled_departure', ''))
    s_arr = _parse_dt(request.POST.get('scheduled_arrival', ''))
    a_dep = _parse_dt(request.POST.get('actual_departure', ''))
    a_arr = _parse_dt(request.POST.get('actual_arrival', ''))
    status = request.POST.get('status', Trip.STATUS_SCHEDULED).strip()
    notes = request.POST.get('notes', '').strip()
    try:
        passenger_count = int(request.POST.get('passenger_count', '0') or 0)
    except ValueError:
        return JsonResponse({'error': 'Passenger count must be a number.'}, status=400)

    bus = None
    if bus_id:
        bus = scoped_buses(request.user).filter(pk=bus_id).first()
        if bus is None:
            return JsonResponse({'error': 'Selected bus is invalid.'}, status=400)
    if not origin:
        return JsonResponse({'error': 'Origin is required.'}, status=400)
    if not destination:
        return JsonResponse({'error': 'Destination is required.'}, status=400)
    if s_dep is None:
        return JsonResponse({'error': 'Scheduled departure is required.'}, status=400)
    if s_arr is None:
        return JsonResponse({'error': 'Scheduled arrival is required.'}, status=400)
    if s_arr <= s_dep:
        return JsonResponse({'error': 'Scheduled arrival must be after departure.'}, status=400)
    if status not in dict(Trip.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status.'}, status=400)
    if passenger_count < 0:
        return JsonResponse({'error': 'Passenger count cannot be negative.'}, status=400)
    if bus and passenger_count > bus.capacity:
        return JsonResponse({'error': f'Passenger count exceeds bus capacity ({bus.capacity}).'}, status=400)

    delay_minutes = 0
    if a_arr and s_arr:
        delay_minutes = max(0, int((a_arr - s_arr).total_seconds() / 60))
        # Auto-escalate: arrived 15+ min late but still marked on-time/en-route
        if delay_minutes >= 15 and status in (Trip.STATUS_ON_TIME, Trip.STATUS_EN_ROUTE, Trip.STATUS_SCHEDULED):
            status = Trip.STATUS_DELAYED
    elif status == Trip.STATUS_DELAYED:
        try:
            delay_minutes = int(request.POST.get('delay_minutes', '0') or 0)
        except ValueError:
            delay_minutes = 0

    trip.bus = bus
    trip.origin = origin
    trip.destination = destination
    trip.route = route or (bus.route if bus else f'{origin} - {destination}')
    trip.scheduled_departure = s_dep
    trip.scheduled_arrival = s_arr
    trip.actual_departure = a_dep
    trip.actual_arrival = a_arr
    trip.status = status
    trip.delay_minutes = max(0, delay_minutes)
    trip.passenger_count = passenger_count
    trip.notes = notes
    if not trip.pk:
        trip.user = request.user
    try:
        trip.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save trip due to a conflict.'}, status=400)
    messages.success(request, f'Trip {trip.origin} -> {trip.destination} {"updated" if is_update else "saved"}.')
    return JsonResponse({'status': 'success', 'id': trip.id, 'is_alert': trip.is_alert})


@login_required(login_url='login')
@require_POST
def trip_delete_ajax(request, pk):
    trip = scoped_trip(request.user, pk)
    label = f'{trip.origin} -> {trip.destination}'
    trip.delete()
    messages.success(request, f'Trip "{label}" deleted.')
    return JsonResponse({'status': 'deleted'})


@login_required(login_url='login')
def alerts_page(request):
    """Trip and Delay Alerts operations board: KPIs, delays chart, fleet status, recent delays."""
    from datetime import timedelta
    trips_qs = scoped_trips(request.user).select_related('bus')
    buses_qs = scoped_buses(request.user)
    incidents_qs = scoped_incidents(request.user)

    alert_statuses = [Trip.STATUS_DELAYED, Trip.STATUS_REROUTED, Trip.STATUS_UNEXPECTED_STOP]
    alert_trips = list(trips_qs.filter(status__in=alert_statuses).order_by('-updated_at')[:50])
    active_delays = trips_qs.filter(status=Trip.STATUS_DELAYED).count()
    rerouted = trips_qs.filter(status=Trip.STATUS_REROUTED).count()
    unexpected = trips_qs.filter(status=Trip.STATUS_UNEXPECTED_STOP).count()
    avg_delay = trips_qs.aggregate(v=Avg('delay_minutes'))['v'] or 0

    fleet_total = buses_qs.count()
    in_service = buses_qs.filter(status=Bus.STATUS_ACTIVE).count()
    in_maintenance = buses_qs.filter(status=Bus.STATUS_MAINTENANCE).count()
    out_of_service = buses_qs.filter(status=Bus.STATUS_INACTIVE).count()
    operational_pct = round(in_service * 100.0 / fleet_total, 1) if fleet_total else 0

    critical_incidents = incidents_qs.filter(
        severity=Incident.SEVERITY_CRITICAL,
        status__in=[Incident.STATUS_REPORTED, Incident.STATUS_RESPONDING],
    ).count()
    open_incidents = incidents_qs.filter(
        status__in=[Incident.STATUS_REPORTED, Incident.STATUS_RESPONDING]
    ).count()

    # Delays by day (last 7 days) per alert category for the bar chart
    today = timezone.localdate()
    days, delayed_series, rerouted_series, stopped_series = [], [], [], []
    for back in range(6, -1, -1):
        day = today - timedelta(days=back)
        days.append(day.strftime('%a'))
        day_trips = trips_qs.filter(scheduled_departure__date=day)
        delayed_series.append(day_trips.filter(status=Trip.STATUS_DELAYED).count())
        rerouted_series.append(day_trips.filter(status=Trip.STATUS_REROUTED).count())
        stopped_series.append(day_trips.filter(status=Trip.STATUS_UNEXPECTED_STOP).count())

    recent_delays = []
    for t in alert_trips[:8]:
        bus = t.bus
        recent_delays.append({
            'bus_number': bus.bus_number if bus else '—',
            'route': t.route or (bus.route if bus else '—'),
            'location': (bus.current_location if bus and bus.current_location else f'{t.origin} - {t.destination}'),
            'delay_minutes': t.delay_minutes,
            'reason': t.notes or 'No reason logged',
            'status': t.status,
            'status_display': t.get_status_display(),
            'updated_at': t.updated_at,
        })

    return render(request, 'trips/alerts.html', {
        'today': today,
        'active_delays': active_delays, 'rerouted': rerouted, 'unexpected': unexpected,
        'alert_count': len(alert_trips),
        'in_service': in_service, 'fleet_total': fleet_total,
        'in_maintenance': in_maintenance, 'out_of_service': out_of_service,
        'operational_pct': operational_pct,
        'avg_delay': round(avg_delay, 1),
        'critical_incidents': critical_incidents, 'open_incidents': open_incidents,
        'delay_days': days, 'delayed_series': delayed_series,
        'rerouted_series': rerouted_series, 'stopped_series': stopped_series,
        'recent_delays': recent_delays,
    })


@login_required(login_url='login')
def reports_page(request):
    """4. Trip Analytics and Reports: completed trips, delays, utilization, route performance."""
    trips_qs = scoped_trips(request.user).select_related('bus')
    buses_qs = scoped_buses(request.user)
    incidents_qs = scoped_incidents(request.user)
    maint_qs = scoped_maintenances(request.user)

    total_trips = trips_qs.count()
    completed = trips_qs.filter(status__in=[Trip.STATUS_COMPLETED, Trip.STATUS_ON_TIME]).count()
    delayed = trips_qs.filter(status=Trip.STATUS_DELAYED).count()
    rerouted = trips_qs.filter(status=Trip.STATUS_REROUTED).count()
    unexpected = trips_qs.filter(status=Trip.STATUS_UNEXPECTED_STOP).count()
    avg_delay = trips_qs.aggregate(v=Avg('delay_minutes'))['v'] or 0
    total_riders = trips_qs.aggregate(v=Sum('passenger_count'))['v'] or 0
    on_time_pct = round(completed * 100.0 / total_trips, 1) if total_trips else 0

    from django.db.models import Count as C
    capacity_total = buses_qs.aggregate(v=Sum('capacity'))['v'] or 0
    occupied_total = sum(b.passengers.count() for b in buses_qs.all())
    utilization_pct = round(occupied_total * 100.0 / capacity_total, 1) if capacity_total else 0

    route_rows = list(
        trips_qs.values('route').annotate(
            trips=C('id'), delayed_trips=C('id', filter=Q(status=Trip.STATUS_DELAYED)),
            avg_delay=Avg('delay_minutes'), riders=Sum('passenger_count'),
        ).order_by('-trips')[:15]
    )
    bus_rows = []
    for b in buses_qs.order_by('bus_number')[:20]:
        occ = b.passengers.count()
        bus_trips = trips_qs.filter(bus=b).count()
        bus_rows.append({
            'bus_number': b.bus_number, 'route': b.route, 'capacity': b.capacity,
            'occupied': occ, 'seats_left': max(0, b.capacity - occ),
            'utilization': round(occ * 100.0 / b.capacity, 1) if b.capacity else 0,
            'trips': bus_trips,
        })

    open_incidents = incidents_qs.filter(status__in=[Incident.STATUS_REPORTED, Incident.STATUS_RESPONDING]).count()
    pending_maint = maint_qs.exclude(status=MaintenanceRecord.STATUS_COMPLETED).count()

    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="vallacar-trip-report.csv"'
        w = csv.writer(resp)
        w.writerow(['Route', 'Trips', 'Delayed', 'Avg delay (min)', 'Riders'])
        for r in route_rows:
            w.writerow([r['route'], r['trips'], r['delayed_trips'], round(r['avg_delay'] or 0, 1), r['riders'] or 0])
        return resp

    # Chart payloads (used by ApexCharts in template)
    status_labels = dict(Trip.STATUS_CHOICES)
    status_breakdown = list(trips_qs.values('status').annotate(n=C('id')).order_by('-n'))
    for row in status_breakdown:
        row['label'] = status_labels.get(row['status'], row['status'].replace('_', ' ').title())
    return render(request, 'trips/reports.html', {
        'total_trips': total_trips, 'completed': completed, 'delayed': delayed,
        'rerouted': rerouted, 'unexpected': unexpected,
        'avg_delay': round(avg_delay, 1), 'total_riders': total_riders,
        'on_time_pct': on_time_pct, 'utilization_pct': utilization_pct,
        'capacity_total': capacity_total, 'occupied_total': occupied_total,
        'route_rows': route_rows, 'bus_rows': bus_rows,
        'open_incidents': open_incidents, 'pending_maint': pending_maint,
        'status_breakdown': status_breakdown,
    })
