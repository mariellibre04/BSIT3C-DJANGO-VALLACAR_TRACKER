import hashlib
import json
import math
import re
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import UUID

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.db import IntegrityError, transaction
from django.db.models import OuterRef, Q, Subquery
from django.utils import timezone

from apps.scoping import scoped_bus, scoped_buses
from django.db.models import Count
from . import terminal_directory
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
    {'name': 'Mabinay', 'keywords': ('mabinay',), 'lat': 9.7264, 'lng': 122.9256},
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

DEFAULT_STAFF_TERMINAL_ID = 'CEBU-SOUTH'

STAFF_TERMINALS = {
    'CEBU-SOUTH': {
        'name': 'CEBU-SOUTH',
        'label': 'CEBU-SOUTH',
        'lat': 10.2958,
        'lng': 123.8934,
    },
}

# Terminals shown as summary cards on the terminal-monitor kiosk.
KIOSK_TERMINAL_NAMES = [
    'Bacolod', 'Kabankalan', 'Mabinay', 'Dumaguete', 'Sipalay', 'San Carlos', 'Hinigaran',
]

# Static fallback data so the webcam time-in / time-out flow can be demonstrated
# before the real bus records are entered. The kiosk refreshes their timeline so
# the demo board always shows today's current time.
ESTIMATED_STOP_MINUTES = 15
STATIC_DEMO_BUSES = [
    {
        'bus_number': '364',
        'plate_number': '84',
        'capacity': 49,
        'route': 'Sipalay-Kabankalan',
        'terminal': 'Sipalay',
        'state': 'en_route',
        'in_minutes': 45,
        'out_minutes': 4,
    },
    {
        'bus_number': '53',
        'plate_number': '78',
        'capacity': 49,
        'route': 'Bacolod-Dumaguete',
        'terminal': 'Bacolod',
        'state': 'en_route',
        'in_minutes': 38,
        'out_minutes': 1,
    },
    {
        'bus_number': 't76775',
        'plate_number': '46745',
        'capacity': 49,
        'route': 'Kabankalan',
        'terminal': 'Kabankalan',
        'state': 'at_terminal',
        'in_minutes': 12,
        'out_minutes': None,
    },
    {
        'bus_number': 'KDM-101',
        'plate_number': 'VTI 1101',
        'capacity': 49,
        'route': 'Kabankalan-Dumaguete',
        'terminal': 'Mabinay',
        'state': 'at_terminal',
        'in_minutes': 7,
        'out_minutes': None,
    },
    {
        'bus_number': 'KDM-102',
        'plate_number': 'VTI 1102',
        'capacity': 49,
        'route': 'Kabankalan-Dumaguete',
        'terminal': 'Bais',
        'state': 'en_route',
        'in_minutes': 26,
        'out_minutes': 3,
    },
    {
        'bus_number': 'BDG-201',
        'plate_number': 'VTI 2201',
        'capacity': 49,
        'route': 'Bacolod-Dumaguete',
        'terminal': 'Kabankalan',
        'state': 'at_terminal',
        'in_minutes': 5,
        'out_minutes': None,
    },
    {
        'bus_number': 'MAB-301',
        'plate_number': 'VTI 3301',
        'capacity': 49,
        'route': 'Mabinay-Dumaguete',
        'terminal': 'Mabinay',
        'state': 'at_terminal',
        'in_minutes': 9,
        'out_minutes': None,
    },
    {
        'bus_number': 'KAB-401',
        'plate_number': 'VTI 4401',
        'capacity': 49,
        'route': 'Kabankalan-Bacolod',
        'terminal': 'Kabankalan',
        'state': 'en_route',
        'in_minutes': 33,
        'out_minutes': 2,
    },
    {
        'bus_number': 'DUM-501',
        'plate_number': 'VTI 5501',
        'capacity': 49,
        'route': 'Dumaguete-Bais',
        'terminal': 'Dumaguete',
        'state': 'at_terminal',
        'in_minutes': 4,
        'out_minutes': None,
    },
    {
        'bus_number': 'SIP-601',
        'plate_number': 'VTI 6601',
        'capacity': 49,
        'route': 'Sipalay-Himamaylan',
        'terminal': 'Sipalay',
        'state': 'en_route',
        'in_minutes': 29,
        'out_minutes': 2,
    },
    {
        'bus_number': 'BAC-701',
        'plate_number': 'VTI 7701',
        'capacity': 49,
        'route': 'Bacolod-San Carlos',
        'terminal': 'Bacolod',
        'state': 'at_terminal',
        'in_minutes': 6,
        'out_minutes': None,
    },
]

KIOSK_BAY_COUNT = 12
KIOSK_STATIC_BAYS = {
    '364': 5,
    '53': 3,
    't76775': 7,
    'KDM-101': 2,
    'KDM-102': 4,
    'BDG-201': 1,
    'MAB-301': 6,
    'KAB-401': 8,
    'DUM-501': 9,
    'SIP-601': 10,
    'BAC-701': 11,
}

KIOSK_STATUS_CLASS = {
    Bus.MOVE_AT_TERMINAL: 'is-at',
    Bus.MOVE_EN_ROUTE: 'is-enroute',
    Bus.MOVE_STOPPED: 'is-delayed',
    Bus.MOVE_DELAYED: 'is-delayed',
    Bus.MOVE_OFF_ROUTE: 'is-delayed',
}


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


def _kiosk_bay(bus):
    """Static bay assignment for the kiosk board."""
    bay = KIOSK_STATIC_BAYS.get(bus.bus_number)
    if bay is None:
        digits = re.sub(r'\D', '', bus.bus_number or '') or str(bus.id or 0)
        bay = (int(digits[-3:]) % KIOSK_BAY_COUNT) + 1
    return f'Bay {bay:02d}'


def _kiosk_board_context(selected_terminal=None):
    """Build the live terminal-monitor board from buses and their last tap.

    When ``selected_terminal`` is a directory entry, only that location's
    available buses and movements are returned. Free-form tap labels are
    matched back to the directory so a bus checked in at ``CEBU-SOUTH`` still
    appears on the Cebu South Bus Terminal kiosk.
    """
    latest_tap_id = (
        BusTerminalTap.objects.filter(bus_id=OuterRef('pk'))
        .order_by('-tapped_at')
        .values('id')[:1]
    )
    buses = list(
        Bus.objects.filter(status=Bus.STATUS_ACTIVE)
        .annotate(
            latest_tap_id=Subquery(latest_tap_id),
            passenger_count=Count('passengers'),
        )
        .order_by('bus_number')
    )
    tap_ids = [bus.latest_tap_id for bus in buses if bus.latest_tap_id]
    latest_taps = {
        tap.bus_id: tap
        for tap in BusTerminalTap.objects.filter(id__in=tap_ids)
    }
    directory_counts = {
        entry['slug']: {'at_terminal': 0, 'inbound': 0, 'departed': 0}
        for entry in terminal_directory.TERMINAL_DIRECTORY
    }
    all_rows = []
    latest_change = None
    signature_parts = []

    for bus in buses:
        tap = latest_taps.get(bus.id)
        is_at = bus.movement_status == Bus.MOVE_AT_TERMINAL
        route_from, route_to = route_endpoints(bus.route)
        dest = route_to['name'] if route_to else ''

        time_in = tap.tapped_at if tap else None
        time_out = tap.left_at if tap else None

        if is_at:
            terminal = tap.terminal_name if tap else (bus.current_location or '')
            when = time_in or (bus.last_gps_update or bus.updated_at)
            estimated = _estimated_departure(tap)
        elif time_out is not None:
            # The bus has timed out: keep showing the stop it just left.
            terminal = tap.terminal_name
            when = time_out
            estimated = None
        else:
            terminal = dest or (tap.terminal_name if tap else '') or (bus.current_location or '')
            when = bus.last_gps_update or bus.updated_at or time_in
            estimated = _estimated_departure(tap)

        terminal = terminal.replace(' Terminal', '').strip()
        if when is not None and (latest_change is None or when > latest_change):
            latest_change = when

        next_destination = None
        arrival = None
        if tap is not None:
            next_destination = _next_destination_for_bus(bus, tap.terminal_name, tap)
            current_terminal = _find_terminal(tap.terminal_name)
            departure_base = time_out or estimated
            arrival = _arrival_estimate(
                current_terminal, next_destination, departure_base
            )

        last_tap_terminal = tap.terminal_name if tap else ''
        tap_entry = terminal_directory.match_terminal(last_tap_terminal)
        terminal_entry = terminal_directory.match_terminal(terminal)
        destination_name = next_destination['name'] if next_destination else ''
        destination_entry = terminal_directory.match_terminal(destination_name)
        if destination_entry is None and not is_at and time_out is None:
            # An en-route bus without a known next stop is heading towards the
            # terminal currently shown in its own row.
            destination_entry = terminal_entry

        seated = bus.passenger_count or 0
        seats_left = max(0, (bus.capacity or 0) - seated)
        item = {
            'number': bus.bus_number,
            'plate': bus.plate_number,
            'route_from': route_from['label'] if route_from else (bus.route or '—'),
            'route_to': route_to['label'] if route_to else '',
            'terminal': terminal or '—',
            'is_hub': terminal == 'Bacolod',
            'time': when,
            'time_in': time_in,
            'time_out': time_out,
            'bay': _kiosk_bay(bus),
            'estimated_departure': estimated,
            'next_destination': destination_name,
            'estimated_arrival': arrival['eta'] if arrival else None,
            'arrival_minutes': arrival['minutes'] if arrival else None,
            'arrival_distance_km': arrival['distance_km'] if arrival else None,
            'status_class': KIOSK_STATUS_CLASS.get(bus.movement_status, 'is-enroute'),
            'status_label': bus.get_movement_status_display(),
            'is_at_terminal': is_at,
            'is_departed': time_out is not None,
            'capacity': bus.capacity or 0,
            'passengers': seated,
            'seats_left': seats_left,
            'is_full': seats_left <= 0,
            'last_tap_terminal': last_tap_terminal,
            '_terminal_slug': terminal_entry['slug'] if terminal_entry else '',
            '_destination_slug': destination_entry['slug'] if destination_entry else '',
            '_tap_slug': tap_entry['slug'] if tap_entry else '',
        }
        signature_parts.append(
            '|'.join([
                str(bus.id),
                bus.bus_number,
                bus.plate_number or '',
                bus.movement_status,
                bus.route or '',
                terminal,
                when.isoformat() if when else '',
                time_in.isoformat() if time_in else '',
                time_out.isoformat() if time_out else '',
                estimated.isoformat() if estimated else '',
                destination_name,
                arrival['eta'].isoformat() if arrival else '',
                f'{seats_left}/{bus.capacity or 0}',
            ])
        )

        all_rows.append(item)
        if is_at:
            if tap_entry is not None:
                directory_counts[tap_entry['slug']]['at_terminal'] += 1
        elif time_out is not None and tap_entry is not None:
            directory_counts[tap_entry['slug']]['departed'] += 1
        if not is_at and destination_entry is not None:
            directory_counts[destination_entry['slug']]['inbound'] += 1

    if selected_terminal is None:
        at_terminal = [row for row in all_rows if row['is_at_terminal']]
        inbound = [row for row in all_rows if not row['is_at_terminal']]
        departed = []
    else:
        slug = selected_terminal['slug']
        at_terminal = [
            row for row in all_rows
            if row['is_at_terminal'] and row['_terminal_slug'] == slug
        ]
        inbound = [
            row for row in all_rows
            if (not row['is_at_terminal'])
            and row['_destination_slug'] == slug
            and row['_tap_slug'] != slug
        ]
        departed = [
            row for row in all_rows
            if (not row['is_at_terminal'])
            and row['is_departed']
            and row['_tap_slug'] == slug
        ]

    at_terminal.sort(key=lambda row: row['time'] or timezone.now(), reverse=True)
    inbound.sort(key=lambda row: row['estimated_arrival'] or row['time'] or timezone.now())
    departed.sort(key=lambda row: row['time'] or timezone.now(), reverse=True)

    featured_entries = (
        [selected_terminal]
        if selected_terminal is not None
        else terminal_directory.featured_terminals()
    )
    terminals = []
    for entry in featured_entries:
        counts = directory_counts[entry['slug']]
        terminals.append({
            'name': entry['name'],
            'terminal': entry['terminal'],
            'slug': entry['slug'],
            'is_hub': entry['hub'],
            'at_terminal': counts['at_terminal'],
            'inbound': counts['inbound'],
            'is_active': bool(
                selected_terminal and entry['slug'] == selected_terminal['slug']
            ),
        })

    groups = []
    for group in terminal_directory.terminal_groups():
        group_terminals = []
        for entry in group['terminals']:
            counts = directory_counts[entry['slug']]
            group_terminals.append({
                'slug': entry['slug'],
                'name': entry['name'],
                'terminal': entry['terminal'],
                'province': entry['province'],
                'region': entry['region'],
                'island': entry['island'],
                'is_hub': entry['hub'],
                'at_terminal': counts['at_terminal'],
                'inbound': counts['inbound'],
                'is_active': bool(
                    selected_terminal and entry['slug'] == selected_terminal['slug']
                ),
                'search': ' '.join((
                    entry['name'],
                    entry['terminal'],
                    entry['province'] or '',
                    entry['region'] or '',
                    entry['island'] or '',
                    *entry['aliases'],
                )).lower(),
            })
        groups.append({
            'region': group['region'],
            'island': group['island'],
            'terminals': group_terminals,
        })

    if latest_change is None:
        updated_label = 'No check-ins yet'
    else:
        clock = timezone.localtime(latest_change).strftime('%I:%M %p').lstrip('0')
        updated_label = f'Updated {clock}'

    signature_parts.append(
        f'selected:{selected_terminal["slug"] if selected_terminal else ""}'
    )
    signature = '\n'.join(signature_parts)
    return {
        'kiosk_terminals': terminals,
        'kiosk_at_terminal': at_terminal,
        'kiosk_inbound': inbound,
        'kiosk_departed': departed,
        'kiosk_selected': selected_terminal,
        'kiosk_selected_slug': selected_terminal['slug'] if selected_terminal else '',
        'kiosk_terminal_groups': groups,
        'kiosk_terminal_count': len(terminal_directory.TERMINAL_DIRECTORY),
        'kiosk_region_count': len(groups),
        'kiosk_total_at': sum(
            counts['at_terminal'] for counts in directory_counts.values()
        ),
        'kiosk_total_inbound': sum(
            counts['inbound'] for counts in directory_counts.values()
        ),
        'kiosk_at_count': len(at_terminal),
        'kiosk_inbound_count': len(inbound),
        'kiosk_departed_count': len(departed),
        'kiosk_available_count': len(at_terminal),
        'kiosk_updated_label': updated_label,
        'kiosk_version': hashlib.sha1(signature.encode('utf-8')).hexdigest() if signature else '',
    }


def terminal_monitor_context(request, selected_terminal=None):
    """QR targets used by the terminal monitor kiosk.

    When a terminal is selected the bus QR codes carry that terminal and
    ``auto=1`` so a scan records the time in/out at that exact terminal.
    """
    auto_suffix = ''
    terminal_query = ''
    if selected_terminal is not None:
        auto_suffix = '?' + urlencode({
            'terminal': selected_terminal['slug'],
            'auto': '1',
        })
        terminal_query = '?' + urlencode({'terminal': selected_terminal['slug']})

    bus_qr_map = {
        bus.bus_number: request.build_absolute_uri(
            reverse('bus:bus_tap', args=[bus.qr_token])
        ) + auto_suffix
        for bus in Bus.objects.all()
    }
    return {
        'kiosk_qr_data': {
            'checkin': (
                request.build_absolute_uri(reverse('bus:conductor_checkin'))
                + terminal_query
            ),
            'scan': (
                request.build_absolute_uri(reverse('bus:bus_scan'))
                + terminal_query
            ),
            'terminal': selected_terminal['name'] if selected_terminal else '',
            'terminal_slug': selected_terminal['slug'] if selected_terminal else '',
            'auto': bool(selected_terminal),
            'buses': bus_qr_map,
        },
    }


def bus_kiosk_page(request, terminal_slug=None):
    """Live airport-style terminal monitor board.

    Without a slug the board shows the nationwide overview. With a slug it is
    a dedicated kiosk for that terminal only.
    """
    seed_static_demo_data()
    selected = None
    if terminal_slug:
        selected = terminal_directory.get_terminal(terminal_slug)
        if selected is None:
            return redirect('bus:bus_kiosk')
    context = terminal_monitor_context(request, selected)
    context.update(_kiosk_board_context(selected))
    return render(request, 'bus/terminal_monitor.html', context)


@never_cache
def bus_kiosk_refresh(request):
    """Return refreshed kiosk fragments after a terminal check-in."""
    _advance_demo_departures()
    selected = None
    terminal_slug = (request.GET.get('terminal') or '').strip()
    if terminal_slug:
        selected = terminal_directory.get_terminal(terminal_slug)
        if selected is None:
            return JsonResponse({'error': 'Unknown terminal'}, status=404)

    context = _kiosk_board_context(selected)
    bus_qr_map = terminal_monitor_context(request, selected)['kiosk_qr_data']['buses']
    return JsonResponse({
        'version': context['kiosk_version'],
        'updated': context['kiosk_updated_label'],
        'selected': context['kiosk_selected_slug'],
        'counts': {
            'at': context['kiosk_at_count'],
            'inbound': context['kiosk_inbound_count'],
            'departed': context['kiosk_departed_count'],
            'available': context['kiosk_available_count'],
            'total_at': context['kiosk_total_at'],
            'total_inbound': context['kiosk_total_inbound'],
        },
        'buses': bus_qr_map,
        'sidebar_html': render_to_string(
            'bus/_kiosk_sidebar_items.html', context, request=request
        ),
        'terminals_html': render_to_string(
            'bus/_kiosk_terminals.html', context, request=request
        ),
        'board_html': render_to_string(
            'bus/_kiosk_board_body.html', context, request=request
        ),
        'ticker_html': render_to_string(
            'bus/_kiosk_ticker_items.html', context, request=request
        ),
    })


def _find_terminal(terminal_name):
    name = (terminal_name or '').strip()
    if not name:
        return None
    lowered = name.lower()
    for terminal in TERMINALS:
        if terminal['name'].lower() == lowered or terminal.get('label', '').lower() == lowered:
            return terminal
    for place in CITY_PLACES:
        if place['label'].lower() == lowered or place['name'].lower() == lowered:
            return {
                'name': place['name'],
                'label': place['name'],
                'lat': place['lat'],
                'lng': place['lng'],
            }
    entry = (
        terminal_directory.get_terminal(name)
        or terminal_directory.match_terminal(name)
    )
    if entry is not None:
        return {
            'name': entry['name'],
            'label': entry['name'],
            'lat': entry['lat'],
            'lng': entry['lng'],
        }
    return None


def _normalize_terminal_key(value):
    return re.sub(r'[^A-Z0-9]+', '-', (value or '').strip().upper()).strip('-')


def _staff_terminal(terminal_id):
    key = _normalize_terminal_key(terminal_id)
    if not key:
        key = DEFAULT_STAFF_TERMINAL_ID
    if key in STAFF_TERMINALS:
        return STAFF_TERMINALS[key]
    for terminal in TERMINALS:
        if _normalize_terminal_key(terminal['name']) == key:
            return {
                'name': terminal['name'],
                'label': terminal['label'],
                'lat': terminal['lat'],
                'lng': terminal['lng'],
            }
    return None


def _staff_terminal_id_for_user(user):
    terminal_id = getattr(user, 'terminal_id', None)
    if terminal_id:
        return str(terminal_id)
    return DEFAULT_STAFF_TERMINAL_ID


def _resolve_scanned_bus(raw):
    token = _extract_qr_token(raw)
    if token is not None:
        bus = Bus.objects.filter(qr_token=token).first()
        if bus is not None:
            return bus
    text = str(raw or '').strip()
    if not text:
        return None
    if text.isdigit():
        bus = Bus.objects.filter(pk=int(text)).first()
        if bus is not None:
            return bus
    return Bus.objects.filter(bus_number__iexact=text).first()


def _record_staff_scan(bus, terminal, scan_type, user=None):
    """Record an IN (time-in) or OUT (time-out) staff scan."""
    if scan_type == 'OUT':
        tap, _closed = _record_departure_tap(bus, terminal, user)
        return tap
    tap, _created = _record_terminal_tap(bus, terminal, user)
    return tap


def _terminal_from_directory(entry):
    """Convert a directory entry to the legacy terminal shape."""
    if entry is None:
        return None
    return {
        'name': entry['terminal'],
        'label': entry['name'],
        'lat': entry['lat'],
        'lng': entry['lng'],
        'slug': entry['slug'],
    }


def _terminal_matches_entry(terminal_name, entry):
    if entry is None:
        return False
    matched = (
        terminal_directory.get_terminal(terminal_name)
        or terminal_directory.match_terminal(terminal_name)
    )
    if matched is not None:
        return matched['slug'] == entry['slug']
    return (
        terminal_directory.normalize_name(terminal_name)
        == terminal_directory.normalize_name(entry['name'])
    )


def _next_terminal_action(bus, entry):
    """What the next tap at this terminal should do."""
    open_tap = _open_tap_for(bus)
    if open_tap is not None and _terminal_matches_entry(open_tap.terminal_name, entry):
        return 'time_out'
    return 'time_in'


def _perform_kiosk_tap(bus, entry, user=None):
    """Automatically time in or time out at a specific terminal.

    A tap at the same terminal closes the open stop (time out). A tap at a
    different terminal closes the previous stop and checks the bus in here.
    """
    terminal = _terminal_from_directory(entry)
    open_tap = _open_tap_for(bus)

    if open_tap is not None and _terminal_matches_entry(open_tap.terminal_name, entry):
        tap, closed = _record_departure_tap(bus, terminal, user)
        return tap, 'time_out', closed, False

    switched = open_tap is not None
    if switched:
        _record_departure_tap(bus, None, user)
    tap, created = _record_terminal_tap(bus, terminal, user)
    return tap, 'time_in', created, switched


def _announce_kiosk_tap(request, bus, entry, tap, action, created, switched):
    label = entry['name']
    if action == 'time_out':
        left_at = timezone.localtime(tap.left_at)
        messages.success(
            request,
            f'Time out recorded: {bus.bus_number} left {label} Terminal at '
            f'{left_at.strftime("%I:%M %p").lstrip("0")}.',
        )
    elif switched:
        departure = _estimated_departure(tap)
        messages.success(
            request,
            f'{bus.bus_number} moved to {label} Terminal. '
            f'Estimated departure '
            f'{timezone.localtime(departure).strftime("%I:%M %p").lstrip("0")}.',
        )
    elif created:
        departure = _estimated_departure(tap)
        messages.success(
            request,
            f'Time in recorded: {bus.bus_number} is at {label} Terminal. '
            f'Estimated departure '
            f'{timezone.localtime(departure).strftime("%I:%M %p").lstrip("0")}.',
        )
    else:
        messages.info(
            request,
            f'{bus.bus_number} is already timed in at {label} Terminal.',
        )


_QR_TOKEN_RE = re.compile(
    r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
    r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
)


def _extract_qr_token(raw):
    """Pull the bus QR token out of a scanned URL or raw token."""
    if not raw:
        return None
    text = raw.strip()
    match = _QR_TOKEN_RE.search(text)
    candidate = match.group(0) if match else text
    try:
        return UUID(candidate)
    except (ValueError, TypeError, AttributeError):
        return None


def _open_tap_for(bus, terminal_name=None):
    """Return the latest tap that has not been timed out yet."""
    taps = bus.terminal_taps.filter(left_at__isnull=True)
    if terminal_name:
        taps = taps.filter(terminal_name=terminal_name)
    return taps.order_by('-tapped_at').first()


def _estimated_departure(tap):
    if tap is None:
        return None
    return tap.tapped_at + timedelta(minutes=ESTIMATED_STOP_MINUTES)


def _next_destination_for_bus(bus, terminal_name, tap=None):
    """Best-effort next stop for a bus based on its route and travel direction.

    Endpoints come from the route text. For an intermediate stop (for example
    Mabinay on Kabankalan-Dumaguete) the previous tap tells us which way the bus
    is heading; otherwise the route's second endpoint is used.
    """
    route_from, route_to = route_endpoints(bus.route)
    if not (route_from and route_to):
        return None
    current = _find_terminal(terminal_name)
    if current is None:
        return None
    current_name = current['name'].lower()
    from_name = route_from['name'].lower()
    to_name = route_to['name'].lower()
    if current_name == from_name:
        return route_to
    if current_name == to_name:
        return route_from
    if tap is not None:
        previous = (
            bus.terminal_taps
            .filter(tapped_at__lt=tap.tapped_at)
            .order_by('-tapped_at')
            .first()
        )
        if previous is not None:
            previous_name = previous.terminal_name.lower()
            if previous_name == to_name:
                return route_from
    return route_to


def _arrival_estimate(current_terminal, destination, start_time):
    """Estimate the clock time the bus reaches its next destination."""
    if not (current_terminal and destination and start_time):
        return None
    road_km = haversine_km(
        current_terminal['lat'], current_terminal['lng'],
        destination['lat'], destination['lng'],
    ) * ROAD_FACTOR
    minutes = int(round(road_km / AVG_SPEED_KMH * 60))
    return {
        'eta': start_time + timedelta(minutes=minutes),
        'minutes': minutes,
        'distance_km': round(road_km, 1),
    }


def _record_terminal_tap(bus, terminal, user=None):
    """Record a time-in for the bus at a terminal.

    If the bus already has an open tap at this terminal we keep that tap so the
    conductor cannot accidentally create a duplicate time-in.
    """
    with transaction.atomic():
        tap = _open_tap_for(bus, terminal['label'])
        created = tap is None
        if created:
            tap = BusTerminalTap.objects.create(
                bus=bus,
                terminal_name=terminal['label'],
                latitude=Decimal(str(terminal['lat'])),
                longitude=Decimal(str(terminal['lng'])),
                user=user if user and user.is_authenticated else None,
            )
        bus.current_location = f"{terminal['label']} Terminal"
        bus.latitude = Decimal(str(terminal['lat']))
        bus.longitude = Decimal(str(terminal['lng']))
        bus.movement_status = Bus.MOVE_AT_TERMINAL
        bus.movement_reason = ''
        bus.last_gps_update = timezone.now()
        bus.save()
    return tap, created


def _record_departure_tap(bus, terminal=None, user=None):
    """Record a time-out by closing the bus's open tap.

    Returns (tap, closed). ``closed`` is False when there was no open tap.
    """
    with transaction.atomic():
        tap = _open_tap_for(bus)
        if tap is None and terminal is not None:
            tap = BusTerminalTap.objects.create(
                bus=bus,
                terminal_name=terminal['label'],
                latitude=Decimal(str(terminal['lat'])),
                longitude=Decimal(str(terminal['lng'])),
                user=user if user and user.is_authenticated else None,
            )
        closed = tap is not None
        now = timezone.now()
        if tap is not None:
            tap.left_at = now
            tap.save(update_fields=['left_at'])
            terminal_label = tap.terminal_name
            latitude = tap.latitude
            longitude = tap.longitude
        else:
            terminal_label = (bus.current_location or '').replace(' Terminal', '').strip()
            latitude = bus.latitude
            longitude = bus.longitude

        bus.current_location = f"En route from {terminal_label} Terminal"
        bus.latitude = latitude
        bus.longitude = longitude
        bus.movement_status = Bus.MOVE_EN_ROUTE
        bus.movement_reason = ''
        bus.last_gps_update = now
        bus.save()
    return tap, closed


def _demo_bus_for(bus_number):
    """Fetch (or create) one of the static demo buses used on the webcam page."""
    demo = next(
        (b for b in STATIC_DEMO_BUSES if b['bus_number'].lower() == (bus_number or '').lower()),
        None,
    )
    if demo is None:
        return None
    bus, _created = Bus.objects.get_or_create(
        bus_number=demo['bus_number'],
        defaults={
            'plate_number': demo['plate_number'],
            'capacity': demo['capacity'],
            'route': demo['route'],
            'status': Bus.STATUS_ACTIVE,
        },
    )
    return bus


def seed_static_demo_data(force=False):
    """Create the placeholder buses and anchor their timeline to today.

    Timestamps are written once from the real Philippine clock and are then
    left untouched. A bus only changes to en route after its estimated
    departure time has passed; it is never re-timed on every request.
    """
    now = timezone.now()
    today = timezone.localdate(now)
    with transaction.atomic():
        for demo in STATIC_DEMO_BUSES:
            terminal = _find_terminal(demo['terminal'])
            if terminal is None:
                continue
            bus, _created = Bus.objects.get_or_create(
                bus_number=demo['bus_number'],
                defaults={
                    'plate_number': demo['plate_number'],
                    'capacity': demo['capacity'],
                    'route': demo['route'],
                    'status': Bus.STATUS_ACTIVE,
                },
            )
            tap = bus.terminal_taps.order_by('-tapped_at').first()
            should_anchor = (
                force
                or tap is None
                or timezone.localdate(tap.tapped_at) != today
            )

            if should_anchor:
                in_minutes = demo.get('in_minutes') or 0
                out_minutes = demo.get('out_minutes')
                tapped_at = now - timedelta(minutes=in_minutes)
                left_at = (
                    now - timedelta(minutes=out_minutes)
                    if out_minutes is not None else None
                )
                if tap is None:
                    tap = BusTerminalTap.objects.create(
                        bus=bus,
                        terminal_name=terminal['label'],
                        latitude=Decimal(str(terminal['lat'])),
                        longitude=Decimal(str(terminal['lng'])),
                    )
                else:
                    tap.terminal_name = terminal['label']
                    tap.latitude = Decimal(str(terminal['lat']))
                    tap.longitude = Decimal(str(terminal['lng']))
                    tap.save(update_fields=['terminal_name', 'latitude', 'longitude'])
                BusTerminalTap.objects.filter(pk=tap.pk).update(
                    tapped_at=tapped_at, left_at=left_at
                )
            else:
                tapped_at = tap.tapped_at
                left_at = tap.left_at
                if left_at is None:
                    estimated = _estimated_departure(tap)
                    if estimated is not None and estimated <= now:
                        left_at = estimated
                        BusTerminalTap.objects.filter(pk=tap.pk).update(left_at=left_at)

            if left_at is None:
                bus.current_location = f"{terminal['label']} Terminal"
                bus.movement_status = Bus.MOVE_AT_TERMINAL
            else:
                bus.current_location = f"En route from {terminal['label']} Terminal"
                bus.movement_status = Bus.MOVE_EN_ROUTE
            bus.latitude = Decimal(str(terminal['lat']))
            bus.longitude = Decimal(str(terminal['lng']))
            bus.movement_reason = ''
            bus.status = Bus.STATUS_ACTIVE
            bus.last_gps_update = now
            bus.save()


def _advance_demo_departures(now=None):
    """Switch placeholder buses to en route once their departure time passes."""
    now = now or timezone.now()
    demo_numbers = [demo['bus_number'] for demo in STATIC_DEMO_BUSES]
    taps = (
        BusTerminalTap.objects
        .filter(bus__bus_number__in=demo_numbers, left_at__isnull=True)
        .select_related('bus')
    )
    for tap in taps:
        estimated = _estimated_departure(tap)
        if estimated is None or estimated > now:
            continue
        BusTerminalTap.objects.filter(pk=tap.pk).update(left_at=estimated)
        if tap.bus.movement_status != Bus.MOVE_EN_ROUTE:
            Bus.objects.filter(pk=tap.bus_id).update(
                movement_status=Bus.MOVE_EN_ROUTE,
                current_location=f"En route from {tap.terminal_name}",
                movement_reason='',
            )


@never_cache
def bus_tap_page(request, token):
    """Bus QR check-in.

    When the QR is opened from a terminal kiosk the terminal is locked and the
    scan automatically records a time in or time out at that terminal.
    """
    bus = get_object_or_404(Bus, qr_token=token)
    requested_slug = (
        request.GET.get('terminal')
        or request.POST.get('terminal_slug')
        or ''
    ).strip()
    entry = terminal_directory.get_terminal(requested_slug) if requested_slug else None
    auto = (request.GET.get('auto') or '').lower() in ('1', 'true', 'yes')
    done = request.GET.get('done') == '1'

    if entry is not None and request.method == 'GET' and auto and not done:
        tap, action, created, switched = _perform_kiosk_tap(
            bus, entry, request.user
        )
        _announce_kiosk_tap(request, bus, entry, tap, action, created, switched)
        query = urlencode({'terminal': entry['slug'], 'done': '1'})
        return redirect(f"{reverse('bus:bus_tap', args=[bus.qr_token])}?{query}")

    if request.method == 'POST':
        if entry is not None:
            tap, action, created, switched = _perform_kiosk_tap(
                bus, entry, request.user
            )
            _announce_kiosk_tap(request, bus, entry, tap, action, created, switched)
            query = urlencode({'terminal': entry['slug'], 'done': '1'})
            return redirect(f"{reverse('bus:bus_tap', args=[bus.qr_token])}?{query}")

        terminal = _find_terminal(request.POST.get('terminal', '').strip())
        if terminal is None:
            messages.error(request, 'Choose a valid terminal.')
        elif request.POST.get('action') == 'time_out':
            tap, closed = _record_departure_tap(bus, terminal, request.user)
            if closed:
                messages.success(
                    request,
                    f'Time out recorded: {bus.bus_number} left {tap.terminal_name} Terminal at '
                    f'{timezone.localtime(tap.left_at).strftime("%I:%M %p").lstrip("0")}.',
                )
            else:
                messages.warning(
                    request,
                    f'{bus.bus_number} has no open time-in at {terminal["label"]} Terminal.',
                )
        else:
            tap, created = _record_terminal_tap(bus, terminal, request.user)
            if created:
                departure = _estimated_departure(tap)
                messages.success(
                    request,
                    f'Time in recorded: {bus.bus_number} is at {terminal["label"]} Terminal. '
                    f'Estimated departure '
                    f'{timezone.localtime(departure).strftime("%I:%M %p").lstrip("0")}.',
                )
            else:
                messages.info(
                    request,
                    f'{bus.bus_number} is already timed in at {terminal["label"]} Terminal.',
                )
        return redirect('bus:bus_tap', token=bus.qr_token)

    open_tap = _open_tap_for(bus)
    taps = bus.terminal_taps.select_related('user')[:10]
    next_action = _next_terminal_action(bus, entry) if entry else ''
    return render(request, 'bus/tap.html', {
        'bus': bus,
        'terminals': TERMINALS,
        'taps': taps,
        'open_tap': open_tap,
        'estimated_departure': _estimated_departure(open_tap),
        'estimated_stop_minutes': ESTIMATED_STOP_MINUTES,
        'terminal_entry': entry,
        'terminal_locked': entry is not None,
        'next_action': next_action,
        'next_action_label': 'Time Out' if next_action == 'time_out' else 'Time In',
        'tap_done': done,
    })


def conductor_checkin_page(request):
    """Public conductor check-in reached from the terminal monitor kiosk QR."""
    buses = Bus.objects.order_by('bus_number')
    selected_number = request.GET.get('bus', '').strip()
    selected_bus = buses.filter(bus_number=selected_number).first()
    requested_slug = (
        request.GET.get('terminal')
        or request.POST.get('terminal_slug')
        or ''
    ).strip()
    entry = terminal_directory.get_terminal(requested_slug) if requested_slug else None

    if request.method == 'POST':
        bus = get_object_or_404(Bus, pk=request.POST.get('bus') or 0)
        if entry is not None:
            tap, action, created, switched = _perform_kiosk_tap(
                bus, entry, request.user
            )
            _announce_kiosk_tap(request, bus, entry, tap, action, created, switched)
            return redirect('bus:bus_tap', token=bus.qr_token)
        terminal = _find_terminal(request.POST.get('terminal', '').strip())
        if terminal is None:
            messages.error(request, 'Choose a valid terminal.')
        elif request.POST.get('action') == 'time_out':
            tap, closed = _record_departure_tap(bus, terminal, request.user)
            if closed:
                messages.success(
                    request,
                    f'Time out recorded: {bus.bus_number} left {tap.terminal_name} Terminal at '
                    f'{timezone.localtime(tap.left_at).strftime("%I:%M %p").lstrip("0")}.',
                )
            else:
                messages.warning(
                    request,
                    f'{bus.bus_number} has no open time-in at {terminal["label"]} Terminal.',
                )
        else:
            tap, created = _record_terminal_tap(bus, terminal, request.user)
            if created:
                departure = _estimated_departure(tap)
                messages.success(
                    request,
                    f'Time in recorded: {bus.bus_number} is at {terminal["label"]} Terminal. '
                    f'Estimated departure '
                    f'{timezone.localtime(departure).strftime("%I:%M %p").lstrip("0")}.',
                )
            else:
                messages.info(
                    request,
                    f'{bus.bus_number} is already timed in at {terminal["label"]} Terminal.',
                )
        return redirect('bus:bus_tap', token=bus.qr_token)

    return render(request, 'bus/conductor_checkin.html', {
        'buses': buses,
        'terminals': TERMINALS,
        'selected_bus': selected_bus,
        'selected_number': selected_number,
        'terminal_entry': entry,
        'terminal_locked': entry is not None,
    })


@never_cache
def bus_scan_page(request):
    """Webcam QR station: scan a bus QR at a terminal to record a tap."""
    seed_static_demo_data()
    taps = list(BusTerminalTap.objects.select_related('bus', 'user')[:8])
    for tap in taps:
        tap.departure = tap.left_at or _estimated_departure(tap)
    terminal_names = {t['name'].lower() for t in TERMINALS}
    city_places = [
        p for p in CITY_PLACES if p['name'].lower() not in terminal_names
    ]
    requested_terminal = request.GET.get('terminal', '').strip()
    locked_terminal = None
    if requested_terminal:
        locked_terminal = (
            terminal_directory.get_terminal(requested_terminal)
            or terminal_directory.match_terminal(requested_terminal)
        )
    return render(request, 'bus/scan.html', {
        'terminals': TERMINALS,
        'city_places': sorted(city_places, key=lambda p: (p['province'], p['name'])),
        'taps': taps,
        'selected_terminal': (
            locked_terminal['terminal'] if locked_terminal else requested_terminal
        ),
        'locked_terminal': locked_terminal,
        'demo_buses': STATIC_DEMO_BUSES,
        'estimated_stop_minutes': ESTIMATED_STOP_MINUTES,
    })


@never_cache
def terminal_scan_page(request):
    """Mobile terminal-staff scanner for bus arrivals and departures."""
    terminal = (
        _staff_terminal(_staff_terminal_id_for_user(request.user))
        or _staff_terminal(DEFAULT_STAFF_TERMINAL_ID)
    )
    return render(request, 'terminal/scan.html', {
        'terminal_id': terminal['name'],
        'terminal_label': terminal['label'],
        'terminal': terminal,
    })


@never_cache
@require_POST
def terminal_checkin_api(request):
    """Record an IN/OUT bus scan from the terminal-staff scanner."""
    if request.content_type and request.content_type.startswith('application/json'):
        try:
            payload = json.loads(request.body or b'{}')
        except (TypeError, ValueError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)
    else:
        payload = request.POST

    if not isinstance(payload, dict):
        return JsonResponse({'error': 'Invalid check-in payload.'}, status=400)

    scan_type = str(payload.get('type', '')).strip().upper()
    if scan_type not in ('IN', 'OUT'):
        return JsonResponse({'error': 'Type must be IN or OUT.'}, status=400)

    raw_bus = payload.get('bus_id') or payload.get('bus') or payload.get('token')
    if not raw_bus:
        return JsonResponse({'error': 'Bus QR code is required.'}, status=400)

    bus = _resolve_scanned_bus(raw_bus)
    if bus is None:
        return JsonResponse({'error': 'That QR code does not match a registered bus.'}, status=404)

    terminal_id = (
        payload.get('terminal_id')
        or _staff_terminal_id_for_user(request.user)
    )
    terminal = _staff_terminal(terminal_id)
    if terminal is None:
        return JsonResponse({'error': 'Unknown terminal.'}, status=400)

    tap = _record_staff_scan(bus, terminal, scan_type, request.user)
    event_time = tap.left_at if scan_type == 'OUT' and tap.left_at else tap.tapped_at
    local_time = timezone.localtime(event_time)
    return JsonResponse({
        'status': 'ok',
        'type': scan_type,
        'bus': {
            'id': bus.id,
            'bus_number': bus.bus_number,
            'plate_number': bus.plate_number,
            'route': bus.route,
            'current_location': bus.current_location,
            'movement_status': bus.movement_status,
        },
        'terminal': terminal['label'],
        'message': (
            f"Bus {bus.bus_number} checked in at {terminal['label']} Terminal."
            if scan_type == 'IN'
            else f"Bus {bus.bus_number} checked out from {terminal['label']} Terminal."
        ),
        'tapped_at': local_time.strftime('%b %d, %Y %I:%M %p'),
        'kiosk_version': _kiosk_board_context()['kiosk_version'],
    })


def _format_clock(value):
    if value is None:
        return None
    return timezone.localtime(value).strftime('%I:%M %p').lstrip('0')


def _scan_tap_payload(bus, tap, status, message):
    time_in = tap.tapped_at if tap else None
    time_out = tap.left_at if tap else None
    estimated = None if time_out else _estimated_departure(tap)
    current_terminal = _find_terminal(tap.terminal_name) if tap else None
    next_destination = (
        _next_destination_for_bus(bus, tap.terminal_name, tap) if tap else None
    )
    departure_base = time_out or estimated
    arrival = (
        _arrival_estimate(current_terminal, next_destination, departure_base)
        if current_terminal and next_destination else None
    )
    return {
        'status': status,
        'bus': {
            'id': bus.id,
            'bus_number': bus.bus_number,
            'plate_number': bus.plate_number,
            'route': bus.route,
            'current_location': bus.current_location,
        },
        'terminal': tap.terminal_name if tap else '',
        'place': tap.terminal_name if tap else '',
        'time_in': _format_clock(time_in),
        'time_out': _format_clock(time_out),
        'estimated_departure': _format_clock(estimated),
        'next_destination': next_destination['name'] if next_destination else '',
        'estimated_arrival': _format_clock(arrival['eta']) if arrival else None,
        'arrival_minutes': arrival['minutes'] if arrival else None,
        'arrival_distance_km': arrival['distance_km'] if arrival else None,
        'tapped_at': (
            timezone.localtime(tap.tapped_at).strftime('%b %d, %Y %I:%M %p')
            if tap else ''
        ),
        'message': message,
    }


@never_cache
@require_POST
def bus_scan_checkin_ajax(request):
    """Webcam scan endpoint supporting time-in, a time-out prompt and time-out.

    The first scan of a bus at a terminal records an automatic time-in. Scanning
    the same bus again returns a prompt so the conductor can choose "Time Out".
    """
    raw_token = request.POST.get('token', '')
    token = _extract_qr_token(raw_token)
    if token is not None:
        bus = Bus.objects.filter(qr_token=token).first()
    elif raw_token.strip():
        return JsonResponse({'error': 'That QR code is not a valid bus code.'}, status=400)
    else:
        demo_number = (request.POST.get('bus_number') or '').strip()
        bus = _demo_bus_for(demo_number) if demo_number else None
        if bus is None and request.POST.get('bus_id'):
            bus = Bus.objects.filter(pk=request.POST.get('bus_id')).first()
    if bus is None:
        return JsonResponse({'error': 'That QR code does not match a registered bus.'}, status=404)

    terminal = _find_terminal((request.POST.get('terminal') or '').strip())
    if terminal is None:
        demo = next(
            (b for b in STATIC_DEMO_BUSES if b['bus_number'].lower() == bus.bus_number.lower()),
            None,
        )
        terminal = _find_terminal(demo['terminal']) if demo else None
    if terminal is None:
        return JsonResponse({'error': 'Choose a valid terminal before scanning.'}, status=400)

    action = (request.POST.get('action') or '').strip().lower()

    if action == 'time_out':
        tap, closed = _record_departure_tap(bus, terminal, request.user)
        if not closed:
            return JsonResponse(
                {'error': f'{bus.bus_number} has no open time-in at {terminal["label"]} Terminal.'},
                status=400,
            )
        return JsonResponse(_scan_tap_payload(
            bus,
            tap,
            'time_out',
            f'Time out: {bus.bus_number} left {tap.terminal_name} Terminal.',
        ))

    open_tap = _open_tap_for(bus)
    if open_tap is not None:
        payload = _scan_tap_payload(
            bus,
            open_tap,
            'prompt',
            f'{bus.bus_number} is already timed in at {open_tap.terminal_name} Terminal. '
            f'Choose Time Out to record the departure.',
        )
        payload['prompt'] = {
            'title': f'Bus {bus.bus_number} is already timed in',
            'terminal': open_tap.terminal_name,
            'time_in': payload['time_in'],
            'estimated_departure': payload['estimated_departure'],
            'actions': ['time_out'],
        }
        return JsonResponse(payload)

    tap, created = _record_terminal_tap(bus, terminal, request.user)
    message = (
        f'Time in: {bus.bus_number} tapped in at {tap.terminal_name} Terminal.'
        if created
        else f'{bus.bus_number} is already timed in at {tap.terminal_name} Terminal.'
    )
    return JsonResponse(_scan_tap_payload(bus, tap, 'time_in', message))


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
        seats_free = max(0, b.capacity - occupied)
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
    estimated arrival time and seat availability. Staff keep GPS editing.
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
