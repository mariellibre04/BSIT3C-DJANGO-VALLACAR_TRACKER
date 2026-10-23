import json
import math
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from apps.scoping import scoped_bus, scoped_buses
from django.db.models import Count
from .models import Bus, BusTerminalTap

MIN_CAPACITY = 1
MAX_CAPACITY = 100


def _parse_capacity(raw):
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _parse_coord(raw, low, high):
    raw = (raw or '').strip() if isinstance(raw, str) else raw
    if raw in (None, ''):
        return None, None
    try:
        value = Decimal(str(raw))
    except (InvalidOperation, ValueError, TypeError):
        return None, 'Enter a valid coordinate.'
    if value < low or value > high:
        return None, f'Coordinate out of range ({low} to {high}).'
    return value, None


# Vallacar / Ceres terminals (Negros / Cebu corridors). Used both for the
# passenger origin-destination picker and to locate a bus on the map when it
# has no live GPS fix yet.
TERMINALS = [
    {'name': 'Bacolod', 'keywords': ('bacolod',), 'lat': 10.6765, 'lng': 122.9509},
    {'name': 'Kabankalan', 'keywords': ('kabankalan', 'kabnakalan'), 'lat': 9.9917, 'lng': 122.8128},
    {'name': 'Dumaguete', 'keywords': ('dumaguete',), 'lat': 9.3072, 'lng': 123.3080},
    {'name': 'San Carlos', 'keywords': ('san carlos', 'sancarlos'), 'lat': 10.4966, 'lng': 123.4224},
    {'name': 'Cadiz', 'keywords': ('cadiz',), 'lat': 10.9586, 'lng': 123.1321},
    {'name': 'Victorias', 'keywords': ('victorias',), 'lat': 10.9000, 'lng': 123.0667},
    {'name': 'Sagay', 'keywords': ('sagay',), 'lat': 10.8917, 'lng': 123.4150},
    {'name': 'Escalante', 'keywords': ('escalante',), 'lat': 10.8333, 'lng': 123.5000},
    {'name': 'Sipalay', 'keywords': ('sipalay',), 'lat': 9.7500, 'lng': 122.4000},
    {'name': 'Himamaylan', 'keywords': ('himamaylan',), 'lat': 10.1003, 'lng': 122.8702},
    {'name': 'Hinigaran', 'keywords': ('hinigaran',), 'lat': 10.0417, 'lng': 122.8567},
    {'name': 'Binalbagan', 'keywords': ('binalbagan',), 'lat': 10.0739, 'lng': 122.8667},
    {'name': 'Bais', 'keywords': ('bais',), 'lat': 9.5917, 'lng': 123.1222},
    {'name': 'Tanjay', 'keywords': ('tanjay',), 'lat': 9.5167, 'lng': 123.1583},
    {'name': 'Bayawan', 'keywords': ('bayawan',), 'lat': 9.3667, 'lng': 122.8000},
    {'name': 'Canlaon', 'keywords': ('canlaon',), 'lat': 10.3833, 'lng': 123.2000},
    {'name': 'La Carlota', 'keywords': ('la carlota', 'lacarlota'), 'lat': 10.4167, 'lng': 122.9167},
    {'name': 'Guihulngan', 'keywords': ('guihulngan',), 'lat': 10.1167, 'lng': 123.2667},
    {'name': 'Cebu', 'keywords': ('cebu',), 'lat': 10.3157, 'lng': 123.8854},
]

for _terminal in TERMINALS:
    _terminal.setdefault('label', _terminal['name'])


def _load_city_places():
    """Load every Philippine city/municipality for the passenger city picker."""
    path = Path(__file__).with_name('data') / 'ph_cities.json'
    try:
        rows = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    places = []
    for row in rows:
        name = (row.get('name') or '').strip()
        province = (row.get('province') or '').strip()
        if not name:
            continue
        places.append({
            'name': name,
            'province': province,
            'label': row.get('label') or (f'{name}, {province}' if province else name),
            'keywords': (name.lower(),),
            'lat': row['lat'],
            'lng': row['lng'],
        })
    return places


CITY_PLACES = _load_city_places()
PLACES = TERMINALS + CITY_PLACES

# Place search must work without the remote geocoder, and must cover every
# city/municipality visible inside the map bounds (Negros, Panay, Cebu, Bohol,
# ...) so searching a place shown on the map finds it.
MAP_LAT_MIN, MAP_LNG_MIN, MAP_LAT_MAX, MAP_LNG_MAX = 8.5, 121.8, 11.5, 124.2


def _inside_map_bounds(place):
    return (MAP_LAT_MIN <= place['lat'] <= MAP_LAT_MAX
            and MAP_LNG_MIN <= place['lng'] <= MAP_LNG_MAX)


def _dedupe_places(places):
    seen, unique = set(), []
    for p in places:
        key = ((p.get('name') or '').strip().lower(), round(p['lat'], 3), round(p['lng'], 3))
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


SEARCH_PLACES = _dedupe_places(
    list(TERMINALS) + [p for p in CITY_PLACES if _inside_map_bounds(p)]
)

# Each entry: (place keywords, lat, lng).
ROUTE_TERMINAL_GPS = [(t['keywords'], t['lat'], t['lng']) for t in TERMINALS]

# Average Ceres liner speed on the highway + road-vs-straight-line factor,
# used for passenger arrival estimates.
AVG_SPEED_KMH = 45
SLOW_SPEED_KMH = 30
ROAD_FACTOR = 1.3
ARRIVED_KM = 1.5


def haversine_km(lat1, lng1, lat2, lng2):
    """Straight-line distance in kilometres between two coordinates."""
    import math
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _project_on_segment(lat, lng, a, b):
    """Project a point onto the a→b segment; return (fraction, distance_km)."""
    scale = math.cos(math.radians((a['lat'] + b['lat']) / 2))
    ax, ay = a['lng'] * scale, a['lat']
    bx, by = b['lng'] * scale, b['lat']
    px, py = lng * scale, lat
    dx, dy = bx - ax, by - ay
    len2 = dx * dx + dy * dy
    if not len2:
        return 0.0, haversine_km(lat, lng, a['lat'], a['lng'])
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / len2))
    plat = a['lat'] + t * (b['lat'] - a['lat'])
    plng = a['lng'] + t * (b['lng'] - a['lng'])
    return t, haversine_km(lat, lng, plat, plng)


def terminal_on_corridor(origin, dest, waiting, max_km=45.0):
    """True when the waiting terminal sits between origin and destination."""
    if not (origin and dest and waiting):
        return False
    t, distance = _project_on_segment(
        waiting['lat'], waiting['lng'], origin, dest
    )
    return 0.02 <= t <= 0.98 and distance <= max_km


def estimate_arrival(bus_lat, bus_lng, dest_lat, dest_lng, movement_status=''):
    """Estimate when a bus reaches a destination terminal.

    Returns dict with minutes, eta datetime, display label and distance —
    or None when coordinates are missing.
    """
    from datetime import timedelta
    if None in (bus_lat, bus_lng, dest_lat, dest_lng):
        return None
    road_km = haversine_km(bus_lat, bus_lng, dest_lat, dest_lng) * ROAD_FACTOR
    now = timezone.now()
    if road_km < ARRIVED_KM:
        return {'minutes': 0, 'eta': now, 'distance_km': round(road_km, 1),
                'label': 'Arriving now', 'detail': 'Bus is at your terminal'}
    speed = SLOW_SPEED_KMH if movement_status == Bus.MOVE_DELAYED else AVG_SPEED_KMH
    minutes = int(round(road_km / speed * 60))
    eta = now + timedelta(minutes=minutes)
    hours, mins = divmod(minutes, 60)
    label = f'~{hours} h {mins} min' if hours else f'~{mins} min'
    return {'minutes': minutes, 'eta': eta, 'distance_km': round(road_km, 1),
            'label': label, 'detail': f'About {round(road_km)} km away'}


def terminal_by_name(name):
    name = (name or '').strip().lower()
    if not name:
        return None
    for t in PLACES:
        if t['name'].lower() == name or t.get('label', '').lower() == name:
            return t
    return None


def route_endpoints(route_text):
    """Split a route like 'Kabankalan - Bacolod' into (from_terminal, to_terminal).

    Returns (None, None) when fewer than two known terminals are found.
    """
    text = (route_text or '').lower()
    hits = []
    for t in TERMINALS:
        for k in t['keywords']:
            idx = text.find(k)
            if idx >= 0:
                hits.append((idx, t))
                break
    if len(hits) < 2:
        return None, None
    hits.sort(key=lambda h: h[0])
    return hits[0][1], hits[-1][1]


def terminal_json(t):
    if not t:
        return None
    return {
        'name': t['name'],
        'label': t.get('label', t['name']),
        'lat': t['lat'],
        'lng': t['lng'],
    }


def _search_places_json():
    """Every place the live-map search can match without the remote geocoder."""
    return [
        {
            'name': p['name'],
            'label': p.get('label') or p['name'],
            'province': p.get('province', ''),
            'lat': p['lat'],
            'lng': p['lng'],
        }
        for p in SEARCH_PLACES
    ]


def _bus_status_context(bus, now=None, reference=None):
    """Return the next departure and passenger-facing delay/stop reason.

    Departure labels are only used for buses waiting at a terminal. Reasons
    use the dispatcher-entered field first, then fall back to trip notes.
    """
    from apps.trips.models import Trip

    now = now or timezone.now()
    trips = Trip.objects.filter(bus=bus)
    upcoming = (
        trips.filter(scheduled_departure__gte=now)
        .order_by('scheduled_departure')
        .first()
    )
    latest = (
        trips.filter(scheduled_departure__lte=now)
        .order_by('-scheduled_departure')
        .first()
    )
    source = reference or latest or upcoming

    departure_source = upcoming
    if departure_source is None and bus.movement_status == Bus.MOVE_AT_TERMINAL:
        # A delayed bus can still be at the terminal after its scheduled slot.
        departure_source = (
            trips.filter(
                actual_departure__isnull=True,
                scheduled_departure__gte=now - timedelta(hours=12),
            )
            .order_by('-scheduled_departure')
            .first()
        )

    departure = None
    if departure_source:
        departure_at = departure_source.scheduled_departure
        if departure_source.delay_minutes:
            departure_at += timedelta(minutes=departure_source.delay_minutes)
        local = timezone.localtime(departure_at)
        time_label = local.strftime('%I:%M %p').lstrip('0')
        today = timezone.localdate()
        if local.date() == today:
            label = time_label
        elif local.date() == today + timedelta(days=1):
            label = f'Tomorrow, {time_label}'
        else:
            label = f'{local:%b} {local.day}, {time_label}'
        departure = {
            'time': time_label,
            'label': label,
            'iso': departure_at.isoformat(),
            'is_delayed': bool(departure_source.delay_minutes),
            'delay': departure_source.delay_minutes,
        }

    reason = (getattr(bus, 'movement_reason', '') or '').strip()
    if not reason and source:
        reason = (source.notes or '').strip()
    if bus.movement_status not in (Bus.MOVE_DELAYED, Bus.MOVE_STOPPED):
        reason = ''
    return upcoming, departure, reason


def first_terminal(text):
    """Return the first known terminal mentioned in a route/location string."""
    text = (text or '').lower()
    best = None
    for t in TERMINALS:
        for k in t['keywords']:
            idx = text.find(k)
            if idx >= 0:
                if best is None or idx < best[0]:
                    best = (idx, t)
                break
    return best[1] if best else None

# Vallacar Bacolod hub — last-resort pin when the route matches no known terminal.
HUB_LAT, HUB_LNG = 10.6765, 122.9509


def bus_map_coords(bus, ignore_gps=False):
    """Return (lat, lng, is_approx) so every bus can be located on the map.

    Live GPS fix when present; otherwise an approximate pin at the route's
    terminal (jittered per bus so stacked buses spread out).
    """
    if not ignore_gps and bus.latitude is not None and bus.longitude is not None:
        return float(bus.latitude), float(bus.longitude), False
    text = f'{bus.current_location or ""} {bus.route or ""}'.lower()
    base = None
    for keywords, lat, lng in ROUTE_TERMINAL_GPS:
        if any(k in text for k in keywords):
            base = (lat, lng)
            break
    if base is None:
        base = (HUB_LAT, HUB_LNG)
    seed = bus.id or 0
    jitter_lat = ((seed * 7) % 5 - 2) * 0.004
    jitter_lng = ((seed * 13) % 5 - 2) * 0.004
    return round(base[0] + jitter_lat, 6), round(base[1] + jitter_lng, 6), True


def _bus_gps_payload(bus, occupied=None, use_fallback=False):
    if occupied is None:
        try:
            occupied = bus.total_passengers
        except AttributeError:
            occupied = bus.passengers.count()
    lat = float(bus.latitude) if bus.latitude is not None else None
    lng = float(bus.longitude) if bus.longitude is not None else None
    is_approx = False
    if use_fallback and (lat is None or lng is None):
        lat, lng, is_approx = bus_map_coords(bus)
    frm, to = route_endpoints(bus.route)
    return {
        'route_from': terminal_json(frm),
        'route_to': terminal_json(to),
        'id': bus.id,
        'bus_number': bus.bus_number,
        'plate_number': bus.plate_number,
        'capacity': bus.capacity,
        'route': bus.route,
        'status': bus.status,
        'current_location': bus.current_location or bus.route,
        'latitude': lat,
        'longitude': lng,
        'is_approx': is_approx,
        'movement_status': bus.movement_status,
        'movement_display': bus.get_movement_status_display(),
        'movement_reason': bus.movement_reason,
        'last_gps_update': bus.last_gps_update.isoformat() if bus.last_gps_update else None,
        'passengers_count': occupied,
        'available_seats': max(0, bus.capacity - occupied),
        'is_full': max(0, bus.capacity - occupied) <= 0,
    }


@login_required(login_url='login')
def bus_list_page(request):
    query = request.GET.get('q', '').strip()
    buses_list = scoped_buses(request.user).annotate(
        total_passengers=Count('passengers')
    ).order_by('bus_number')
    if query:
        buses_list = buses_list.filter(
            Q(bus_number__icontains=query) |
            Q(plate_number__icontains=query) |
            Q(route__icontains=query) |
            Q(current_location__icontains=query)
        )
    paginator = Paginator(buses_list, 10)
    buses = paginator.get_page(request.GET.get('page', 1))
    for b in buses.object_list:
        b.seats_left = max(0, b.capacity - b.total_passengers)
    return render(request, 'bus/list.html', {'buses': buses, 'query': query})


@login_required(login_url='login')
def bus_list_ajax(request):
    query = request.GET.get('q', '').strip()
    buses_list = scoped_buses(request.user).annotate(
        total_passengers=Count('passengers')
    ).order_by('bus_number')
    if query:
        buses_list = buses_list.filter(
            Q(bus_number__icontains=query) |
            Q(plate_number__icontains=query) |
            Q(route__icontains=query) |
            Q(current_location__icontains=query)
        )
    paginator = Paginator(buses_list, 10)
    buses = paginator.get_page(request.GET.get('page', 1))
    data = []
    for b in buses.object_list:
        occupied = b.total_passengers
        data.append(_bus_gps_payload(b, occupied))
    return JsonResponse({
        'data': data,
        'has_next': buses.has_next(),
        'has_prev': buses.has_previous(),
        'page': buses.number,
        'pages': buses.paginator.num_pages,
        'total': buses.paginator.count,
    })


def bus_get_ajax(request, pk):
    if request.user.is_authenticated:
        bus = scoped_bus(request.user, pk)
    else:
        bus = get_object_or_404(Bus, pk=pk)
    return JsonResponse(_bus_gps_payload(bus))


def bus_kiosk_page(request):
    """Airport-style terminal monitor board for passengers (static design)."""
    return render(request, 'bus/terminal_monitor.html')


@never_cache
def bus_tap_page(request, token):
    """Conductor check-in: the bus QR opens this page, the conductor picks the
    terminal they are at and the tap is recorded on the bus."""
    bus = get_object_or_404(Bus, qr_token=token)

    if request.method == 'POST':
        terminal_name = request.POST.get('terminal', '').strip()
        terminal = next((t for t in TERMINALS if t['name'] == terminal_name), None)
        if terminal is None:
            messages.error(request, 'Choose a valid terminal.')
        else:
            with transaction.atomic():
                BusTerminalTap.objects.create(
                    bus=bus,
                    terminal_name=terminal['label'],
                    latitude=Decimal(str(terminal['lat'])),
                    longitude=Decimal(str(terminal['lng'])),
                    user=request.user if request.user.is_authenticated else None,
                )
                bus.current_location = f"{terminal['label']} Terminal"
                bus.latitude = Decimal(str(terminal['lat']))
                bus.longitude = Decimal(str(terminal['lng']))
                bus.movement_status = Bus.MOVE_AT_TERMINAL
                bus.movement_reason = ''
                bus.last_gps_update = timezone.now()
                bus.save()
            messages.success(
                request,
                f'Tap recorded: {bus.bus_number} is at {terminal["label"]} Terminal.',
            )
            return redirect('bus:bus_tap', token=bus.qr_token)

    taps = bus.terminal_taps.select_related('user')[:10]
    return render(request, 'bus/tap.html', {
        'bus': bus,
        'terminals': TERMINALS,
        'taps': taps,
    })


@login_required(login_url='login')
@require_POST
def bus_save_ajax(request):
    bus_id = request.POST.get('id')
    if bus_id:
        bus = scoped_bus(request.user, bus_id)
        is_update = True
    else:
        bus = Bus()
        is_update = False

    bus_number = request.POST.get('bus_number', '').strip()
    plate_number = request.POST.get('plate_number', '').strip()
    capacity = request.POST.get('capacity', '').strip()
    route = request.POST.get('route', '').strip()
    status = request.POST.get('status', Bus.STATUS_ACTIVE).strip()
    current_location = request.POST.get('current_location', '').strip()
    movement_status = request.POST.get('movement_status', Bus.MOVE_AT_TERMINAL).strip()
    movement_reason = request.POST.get('movement_reason', '').strip()
    latitude, lat_error = _parse_coord(request.POST.get('latitude', ''), Decimal('-90'), Decimal('90'))
    longitude, lng_error = _parse_coord(request.POST.get('longitude', ''), Decimal('-180'), Decimal('180'))

    if not bus_number:
        return JsonResponse({'error': 'Bus number is required.'}, status=400)
    if not plate_number:
        return JsonResponse({'error': 'Plate number is required.'}, status=400)
    if not capacity:
        return JsonResponse({'error': 'Capacity is required.'}, status=400)
    capacity_value = _parse_capacity(capacity)
    if capacity_value is None or capacity_value < MIN_CAPACITY or capacity_value > MAX_CAPACITY:
        return JsonResponse(
            {'error': f'Capacity must be a number between {MIN_CAPACITY} and {MAX_CAPACITY}.'},
            status=400,
        )
    if not route:
        return JsonResponse({'error': 'Route is required.'}, status=400)
    if status not in dict(Bus.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status.'}, status=400)
    if movement_status not in dict(Bus.MOVEMENT_CHOICES):
        return JsonResponse({'error': 'Invalid movement status.'}, status=400)
    if lat_error:
        return JsonResponse({'error': f'Latitude: {lat_error}'}, status=400)
    if lng_error:
        return JsonResponse({'error': f'Longitude: {lng_error}'}, status=400)
    if (latitude is None) != (longitude is None):
        return JsonResponse({'error': 'Latitude and longitude must be set together.'}, status=400)

    dup = Bus.objects.filter(Q(bus_number=bus_number) | Q(plate_number=plate_number))
    if bus_id:
        dup = dup.exclude(pk=bus_id)
    if dup.filter(bus_number=bus_number).exists():
        return JsonResponse({'error': 'That bus number already exists.'}, status=400)
    if dup.filter(plate_number=plate_number).exists():
        return JsonResponse({'error': 'That plate number already exists.'}, status=400)

    if bus_id:
        occupied = bus.passengers.count()
        if capacity_value < occupied:
            return JsonResponse(
                {'error': f'Capacity cannot be less than assigned passengers ({occupied}).'},
                status=400,
            )

    gps_changed = (
        (bus.pk is None and (current_location or latitude is not None))
        or (bus.pk and (
            bus.current_location != current_location
            or bus.movement_status != movement_status
            or bus.movement_reason != movement_reason
            or (str(bus.latitude) if bus.latitude is not None else None) != (str(latitude) if latitude is not None else None)
            or (str(bus.longitude) if bus.longitude is not None else None) != (str(longitude) if longitude is not None else None)
        ))
    )
    bus.bus_number = bus_number
    bus.plate_number = plate_number
    bus.capacity = capacity_value
    bus.route = route
    bus.status = status
    bus.current_location = current_location
    bus.latitude = latitude
    bus.longitude = longitude
    bus.movement_status = movement_status
    bus.movement_reason = movement_reason
    if gps_changed:
        bus.last_gps_update = timezone.now()
    if not bus.pk:
        bus.user = request.user

    try:
        bus.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save bus due to a conflict.'}, status=400)

    messages.success(
        request,
        f'Bus "{bus.bus_number}" has been {"updated" if is_update else "saved"} successfully.'
    )
    payload = _bus_gps_payload(bus)
    payload['status'] = 'success'
    return JsonResponse(payload)


@login_required(login_url='login')
@require_POST
def bus_delete_ajax(request, pk):
    bus = scoped_bus(request.user, pk)
    name = bus.bus_number
    bus.delete()
    messages.success(request, f'Bus "{name}" has been deleted successfully.')
    return JsonResponse({'status': 'deleted'})


ROUTE_PALETTE = [
    '#C1121F', '#2563eb', '#16a34a', '#9333ea',
    '#ea580c', '#0891b2', '#be123c', '#4d7c0f',
]

def build_eta_results(buses, origin, dest, waiting, today, now):
    """Assigned buses for an origin → destination corridor.

    Each result carries the live position, estimated arrival at the waiting
    place and destination, free seats and the next scheduled trip.
    """
    from apps.bookings.models import active_holds
    from apps.trips.models import Trip

    results = []
    corridor_match = terminal_on_corridor(origin, dest, waiting)
    for b in buses:
        text = f'{b.route or ""}'.lower()
        frm, to = route_endpoints(b.route)
        endpoints_match = bool(
            frm and to
            and {frm['name'], to['name']} == {origin['name'], dest['name']}
        )
        text_match = (
            any(k in text for k in origin['keywords'])
            or any(k in text for k in dest['keywords'])
        )
        route_has_waiting = any(k in text for k in waiting['keywords'])
        # Relevant when the bus serves the requested corridor and the waiting
        # place is either named on the route or lies between the endpoints
        # (e.g. Himamaylan is on the Bacolod → Dumaguete highway).
        if not (endpoints_match or text_match):
            continue
        if not (route_has_waiting or corridor_match):
            continue
        occupied = b.total_passengers or 0
        lat, lng, is_approx = bus_map_coords(b)
        if not (8.4 <= lat <= 11.6 and 121.7 <= lng <= 124.3):
            lat, lng, is_approx = bus_map_coords(b, ignore_gps=True)
        eta_wait = estimate_arrival(lat, lng, waiting['lat'], waiting['lng'], b.movement_status)
        eta_dest = estimate_arrival(lat, lng, dest['lat'], dest['lng'], b.movement_status)
        seats_free = max(0, b.capacity - occupied - active_holds(b.id))
        trip = (Trip.objects.filter(bus=b, scheduled_departure__date=today)
                .order_by('scheduled_departure'))
        upcoming = trip.filter(scheduled_departure__gte=now).first() or trip.last()
        trip_info = None
        if upcoming:
            dep = timezone.localtime(upcoming.scheduled_departure).strftime('%I:%M %p').lstrip('0')
            arr = timezone.localtime(upcoming.scheduled_arrival).strftime('%I:%M %p').lstrip('0')
            trip_info = {
                'scheduled': f'{dep} → {arr}',
                'status': upcoming.get_status_display(),
                'is_late': upcoming.status in (Trip.STATUS_DELAYED, Trip.STATUS_REROUTED, Trip.STATUS_UNEXPECTED_STOP),
                'delay': upcoming.delay_minutes,
            }
        _status_trip, departure, reason = _bus_status_context(b, now, reference=upcoming)
        nearby = bool(eta_wait and eta_wait['minutes'] <= 45)
        results.append({
            'bus_id': b.id, 'bus_number': b.bus_number, 'plate_number': b.plate_number,
            'route': b.route, 'current_location': b.current_location or b.route,
            'movement_status': b.movement_status,
            'movement_display': b.get_movement_status_display(),
            'movement_reason': b.movement_reason,
            'departure': departure, 'reason': reason,
            'is_approx': is_approx, 'lat': lat, 'lng': lng,
            'capacity': b.capacity, 'occupied': occupied, 'seats_free': seats_free,
            'eta_wait': eta_wait, 'eta_dest': eta_dest, 'nearby': nearby, 'trip': trip_info,
        })
    results.sort(key=lambda r: (r['eta_wait'] is None, r['eta_wait']['minutes'] if r['eta_wait'] else 0))
    return results


def eta_map_json(results, waiting):
    """Payload the Leaflet map on the tracking pages renders."""
    buses = []
    for r in results:
        frm, to = route_endpoints(r['route'])
        buses.append({
            'bus_id': r.get('bus_id'),
            'bus_number': r['bus_number'],
            'route': r['route'],
            'lat': r['lat'], 'lng': r['lng'],
            'seats_free': r['seats_free'],
            'is_approx': r['is_approx'],
            'movement_status': r.get('movement_status'),
            'departure': r.get('departure'),
            'reason': r.get('reason'),
            'route_from': terminal_json(frm),
            'route_to': terminal_json(to),
        })
    return json.dumps({
        'waiting': {'name': waiting['name'], 'lat': waiting['lat'], 'lng': waiting['lng']} if waiting else None,
        'buses': buses,
        'terminals': [terminal_json(t) for t in TERMINALS],
    })


def _find_search_place(query):
    """Resolve a typed place name to a known map place (for the no-JS form)."""
    q = (query or '').strip().lower()
    if not q:
        return None
    for p in SEARCH_PLACES:
        if (p.get('name') or '').lower() == q or (p.get('label') or '').lower() == q:
            return p
    for p in SEARCH_PLACES:
        if q in (p.get('name') or '').lower() or q in (p.get('label') or '').lower():
            return p
    return None


def map_all_buses_json(buses, waiting, search_target=None):
    """Map payload listing every active bus with its movement status label."""
    items = []
    now = timezone.now()
    for b in buses:
        occupied = getattr(b, 'total_passengers', None)
        if occupied is None:
            occupied = b.passengers.count()
        lat, lng, is_approx = bus_map_coords(b)
        # Keep every bus on-screen: ignore GPS fixes outside the Negros region.
        if not (8.4 <= lat <= 11.6 and 121.7 <= lng <= 124.3):
            lat, lng, is_approx = bus_map_coords(b, ignore_gps=True)
        frm, to = route_endpoints(b.route)
        if frm is None:
            frm = first_terminal(f'{b.current_location or ""} {b.route or ""}')
        if frm is None:
            frm = terminal_by_name('Bacolod')
        if to is None:
            to = terminal_by_name('Dumaguete') if frm['name'] != 'Dumaguete' else terminal_by_name('Bacolod')
        _status_trip, departure, reason = _bus_status_context(b, now)
        items.append({
            'bus_id': b.id,
            'bus_number': b.bus_number,
            'route': b.route,
            'lat': lat,
            'lng': lng,
            'is_approx': is_approx,
            'seats_free': max(0, b.capacity - occupied),
            'movement_status': b.movement_status,
            'movement_display': b.get_movement_status_display(),
            'movement_reason': b.movement_reason,
            'departure': departure,
            'reason': reason,
            'bus_status': b.status,
            'route_from': terminal_json(frm),
            'route_to': terminal_json(to),
        })
    return json.dumps({
        'waiting': {'name': waiting['name'], 'lat': waiting['lat'], 'lng': waiting['lng']} if waiting else None,
        'buses': items,
        'terminals': [terminal_json(t) for t in TERMINALS],
        'places': _search_places_json(),
        'search_target': search_target,
    })


def _resolve_trip_params(request):
    origin_name = request.GET.get('from', '').strip() or 'Kabankalan'
    dest_name = request.GET.get('to', '').strip() or 'Bacolod'
    waiting_name = request.GET.get('waiting', '').strip() or origin_name
    return origin_name, dest_name, waiting_name


@never_cache
def bus_map_page(request):
    """Live GPS tracking + ETA board (public, no login).

    Passengers pick From / To / I-am-waiting-in, then watch the assigned
    Ceres liners approach the waiting terminal on the live map, with an
    estimated arrival time, seat availability and a Book button. Staff keep
    GPS editing.
    """
    is_admin = request.user.is_authenticated
    origin_name, dest_name, waiting_name = _resolve_trip_params(request)
    origin = terminal_by_name(origin_name)
    dest = terminal_by_name(dest_name)
    waiting = terminal_by_name(waiting_name)

    results, error = [], None
    today = timezone.localdate()
    now = timezone.now()
    buses_qs = scoped_buses(request.user) if is_admin else Bus.objects.all()
    active_buses = list(
        buses_qs.annotate(total_passengers=Count('passengers'))
        .filter(status=Bus.STATUS_ACTIVE)
        .order_by('bus_number')
    )
    if origin is None or dest is None or waiting is None:
        error = 'Please select a valid origin, destination, and waiting place.'
    elif origin.get('label') == dest.get('label'):
        error = 'Origin and destination must be different terminals.'
    else:
        results = build_eta_results(active_buses, origin, dest, waiting, today, now)

    search_query = request.GET.get('place', '').strip()
    search_place = _find_search_place(search_query)
    search_target = None
    if search_place:
        search_target = {
            'name': search_place['name'],
            'lat': search_place['lat'],
            'lng': search_place['lng'],
        }

    return render(request, 'bus/map.html', {
        'terminals': PLACES,
        'origin_name': origin.get('label', origin['name']) if origin else origin_name,
        'dest_name': dest.get('label', dest['name']) if dest else dest_name,
        'waiting_name': waiting.get('label', waiting['name']) if waiting else waiting_name,
        'results': results, 'error': error,
        'today': today, 'now': timezone.localtime(now),
        'map_json': map_all_buses_json(active_buses, waiting, search_target),
        'movement_choices': Bus.MOVEMENT_CHOICES,
        'is_admin': is_admin,
        'search_query': search_query,
        'default_lat': 12.8797, 'default_lng': 121.7740,
    })


def bus_locations_ajax(request):
    """JSON feed for the live map: location, route, movement, seats.

    Public read-only. Buses without a GPS fix get an approximate
    route-terminal pin so every available bus is located on the map
    (flagged with is_approx).
    """
    buses_qs = scoped_buses(request.user) if request.user.is_authenticated else Bus.objects.all()
    buses = buses_qs.annotate(total_passengers=Count('passengers')).order_by('bus_number')
    return JsonResponse({'buses': [_bus_gps_payload(b, b.total_passengers, use_fallback=True) for b in buses]})


NEGROS_VIEWBOX = '121.8,8.5,124.2,11.5'  # lon_min, lat_min, lon_max, lat_max


def _local_place_matches(query, limit=8):
    """Match known places locally so search still works without the geocoder.

    Covers the Vallacar terminals plus every Negros city/municipality from
    ``ph_cities.json``. Results are ordered from exact to partial matches.
    """
    q = (query or '').strip().lower()
    if not q:
        return []

    scored = []
    for t in SEARCH_PLACES:
        name = (t.get('name') or '').lower()
        label = (t.get('label') or '').lower()
        province = (t.get('province') or '').lower()
        terms = tuple(x for x in (name, label, province) + tuple(t.get('keywords') or ()) if x)
        if not terms:
            continue

        if q == name:
            score = 0
        elif name.startswith(q):
            score = 1
        elif q in name:
            score = 2
        elif name in q:
            score = 3
        elif any(q in term for term in terms):
            score = 4
        else:
            continue
        scored.append((score, len(name), t))

    scored.sort(key=lambda item: (item[0], item[1]))
    matches, seen = [], set()
    for _score, _length, t in scored:
        province = (t.get('province') or '').strip()
        key = (t['name'].lower(), round(t['lat'], 3), round(t['lng'], 3))
        if key in seen:
            continue
        seen.add(key)
        display_name = (
            f"{t['name']}, {province}, Philippines" if province
            else f"{t['name']}, Negros Island, Philippines"
        )
        matches.append({
            'lat': t['lat'], 'lon': t['lng'],
            'display_name': display_name,
            'local': True,
        })
        if len(matches) >= limit:
            break
    return matches


def geocode_ajax(request):
    """Place search proxy for the live map.

    Uses Nominatim (server-side, with a proper User-Agent) and falls back to
    the built-in terminal list when the remote geocoder is unavailable.
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    cache_key = 'negros-geocode:' + query.lower()
    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse({'results': cached})

    results = _local_place_matches(query)
    remote_failed = False

    params = {
        'format': 'json', 'limit': 8, 'q': query,
        'viewbox': NEGROS_VIEWBOX, 'bounded': 1,
        'countrycodes': 'ph', 'addressdetails': 0,
    }
    try:
        req = Request(
            'https://nominatim.openstreetmap.org/search?' + urlencode(params),
            headers={
                'User-Agent': 'VallacarTracker/1.0 (student project; live map place search)',
                'Accept-Language': 'en',
            },
        )
        with urlopen(req, timeout=6) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
        for item in payload:
            try:
                lat, lon = float(item['lat']), float(item['lon'])
            except (KeyError, TypeError, ValueError):
                continue
            results.append({
                'lat': lat, 'lon': lon,
                'display_name': item.get('display_name') or query,
                'local': False,
            })
    except (URLError, OSError, ValueError, json.JSONDecodeError):
        remote_failed = True

    # Drop duplicates (same place returned by both sources).
    seen, unique = set(), []
    for place in results:
        key = (round(place['lat'], 3), round(place['lon'], 3))
        if key in seen:
            continue
        seen.add(key)
        unique.append(place)

    if not remote_failed:
        cache.set(cache_key, unique, 60 * 60)
    return JsonResponse({'results': unique, 'local_only': remote_failed})


@login_required(login_url='login')
@require_POST
def bus_gps_update_ajax(request, pk):
    """Quick GPS ping: update location / coordinates / movement from the map."""
    bus = scoped_bus(request.user, pk)
    current_location = request.POST.get('current_location', '').strip()
    movement_status = request.POST.get('movement_status', '').strip() or bus.movement_status
    movement_reason = request.POST.get('movement_reason')
    latitude, lat_error = _parse_coord(request.POST.get('latitude', ''), Decimal('-90'), Decimal('90'))
    longitude, lng_error = _parse_coord(request.POST.get('longitude', ''), Decimal('-180'), Decimal('180'))
    if movement_status not in dict(Bus.MOVEMENT_CHOICES):
        return JsonResponse({'error': 'Invalid movement status.'}, status=400)
    if lat_error:
        return JsonResponse({'error': f'Latitude: {lat_error}'}, status=400)
    if lng_error:
        return JsonResponse({'error': f'Longitude: {lng_error}'}, status=400)
    if (latitude is None) != (longitude is None):
        return JsonResponse({'error': 'Latitude and longitude must be set together.'}, status=400)
    if current_location:
        bus.current_location = current_location
    if latitude is not None:
        bus.latitude = latitude
        bus.longitude = longitude
    bus.movement_status = movement_status
    if movement_reason is not None:
        bus.movement_reason = movement_reason.strip()
    bus.last_gps_update = timezone.now()
    bus.save(update_fields=['current_location', 'latitude', 'longitude', 'movement_status', 'movement_reason', 'last_gps_update', 'updated_at'])
    messages.success(request, f'GPS for bus "{bus.bus_number}" updated.')
    payload = _bus_gps_payload(bus)
    payload['status'] = 'updated'
    return JsonResponse(payload)


def passenger_eta_page(request):
    """Public passenger board: going from A to B? See the assigned Ceres
    liners on that route with estimated arrival — no more waiting all day.

    Read-only and public (no login) so riders can check before leaving home.

    Riders pick where they are waiting; each assigned bus shows its live
    position, estimated arrival at the waiting place, free seats, and a
    Book button. Bookings notify the assigned driver / conductor.
    """
    origin_name, dest_name, waiting_name = _resolve_trip_params(request)
    origin = terminal_by_name(origin_name)
    dest = terminal_by_name(dest_name)
    waiting = terminal_by_name(waiting_name)

    results, error = [], None
    today = timezone.localdate()
    now = timezone.now()
    if origin is None or dest is None or waiting is None:
        error = 'Please select a valid origin, destination, and waiting place.'
    elif origin.get('label') == dest.get('label'):
        error = 'Origin and destination must be different terminals.'
    else:
        buses = list(
            Bus.objects.annotate(total_passengers=Count('passengers'))
            .filter(status=Bus.STATUS_ACTIVE)
            .order_by('bus_number')
        )
        results = build_eta_results(buses, origin, dest, waiting, today, now)

    return render(request, 'bus/eta.html', {
        'terminals': PLACES, 'origin_name': origin.get('label', origin['name']) if origin else origin_name,
        'dest_name': dest.get('label', dest['name']) if dest else dest_name,
        'waiting_name': waiting.get('label', waiting['name']) if waiting else waiting_name,
        'results': results, 'error': error, 'today': today, 'now': timezone.localtime(now),
        'map_json': eta_map_json(results, waiting),
    })
