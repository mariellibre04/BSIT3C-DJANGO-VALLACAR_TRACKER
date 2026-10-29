"""Route matching, stop-sequence filtering, and ETA calculation."""

import math
import re
import unicodedata
from datetime import timedelta

from django.utils import timezone

from .route_config import (
    FIXED_CONDUCTOR_PROMPT,
    ROUTE_DEFINITIONS,
    TERMINAL_MASTER_LIST,
)

INVALID_STOP_MESSAGE = 'Invalid stop for this route — verify route configuration.'
ROAD_FACTOR = 1.3

_DROP_TOKENS = {
    'terminal', 'terminals', 'bus', 'buses', 'city', 'of', 'the', 'and',
    'inc', 'corp', 'co', 'stop', 'station',
}


def normalize_place(value):
    """Normalize a terminal/stop/route name for safe matching."""
    text = unicodedata.normalize('NFKD', (value or '').lower())
    text = ''.join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r'\([^)]*\)', ' ', text)
    text = text.replace('&', ' and ')
    tokens = [token for token in re.findall(r'[a-z0-9]+', text) if token]
    meaningful = [token for token in tokens if token not in _DROP_TOKENS]
    return ' '.join(meaningful or tokens)


def _alias_list(value):
    return [part.strip() for part in (value or '').split(',') if part.strip()]


def haversine_km(lat1, lng1, lat2, lng2):
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def seed_transit_data(force=False):
    """Create/update the terminal master list and validated route sequences."""
    from .models import Route, RouteStop, Terminal

    if not force and Route.objects.exists() and Terminal.objects.exists():
        return

    terminals = {}
    for entry in TERMINAL_MASTER_LIST:
        terminal, _created = Terminal.objects.update_or_create(
            name=entry['name'],
            defaults={
                'code': entry.get('code', ''),
                'city': entry.get('city', ''),
                'province': entry.get('province', ''),
                'latitude': entry['lat'],
                'longitude': entry['lng'],
                'is_owned_terminal': entry.get('is_owned_terminal', False),
                'is_major_stop': entry.get('is_major_stop', True),
                'source': entry.get('source', ''),
                'aliases': entry.get('aliases', ''),
            },
        )
        terminals[entry['name']] = terminal

    for definition in ROUTE_DEFINITIONS:
        origin = terminals.get(definition['origin'])
        destination = terminals.get(definition['destination'])
        if origin is None or destination is None:
            continue

        route, _created = Route.objects.update_or_create(
            name=definition['name'],
            defaults={
                'origin': origin,
                'destination': destination,
                'validation_status': definition['validation_status'],
                'validation_note': definition.get('validation_note', ''),
                'source': definition.get('source', ''),
                'aliases': definition.get('aliases', ''),
            },
        )

        RouteStop.objects.filter(route=route).delete()
        previous_entry = None
        route_stops = []
        for index, stop in enumerate(definition['stops'], start=1):
            terminal = terminals.get(stop['name'])
            if terminal is None:
                previous_entry = None
                continue

            distance = stop.get('distance_km')
            if distance is None:
                if previous_entry is None:
                    distance = 0
                else:
                    distance = haversine_km(
                        previous_entry['lat'], previous_entry['lng'],
                        stop['lat'] if 'lat' in stop else terminal.latitude,
                        stop['lng'] if 'lng' in stop else terminal.longitude,
                    ) * ROAD_FACTOR

            route_stops.append(RouteStop(
                route=route,
                terminal=terminal,
                sequence=index,
                distance_from_previous_km=round(float(distance), 2),
                average_speed_kmh=int(stop.get('speed_kmh') or 45),
            ))
            previous_entry = {
                'lat': float(terminal.latitude),
                'lng': float(terminal.longitude),
            }

        RouteStop.objects.bulk_create(route_stops)


def ensure_transit_seed():
    """Make sure the master list exists without rewriting it on every request."""
    from .models import Route, Terminal

    if not Route.objects.exists() or not Terminal.objects.exists():
        seed_transit_data()


def find_route_for_bus(bus):
    """Find the configured Route whose name/alias matches ``bus.route``."""
    from .models import Route

    wanted = normalize_place(getattr(bus, 'route', ''))
    if not wanted:
        return None
    for route in Route.objects.prefetch_related('stops__terminal'):
        candidates = [route.name, *_alias_list(route.aliases)]
        if any(normalize_place(candidate) == wanted for candidate in candidates):
            return route
    return None


def find_stop(route, value):
    """Find a route stop by terminal name or alias."""
    if route is None:
        return None
    wanted = normalize_place(value)
    if not wanted:
        return None
    for stop in route.stops.select_related('terminal').all():
        terminal = stop.terminal
        candidates = [terminal.name, *_alias_list(terminal.aliases)]
        if any(normalize_place(candidate) == wanted for candidate in candidates):
            return stop
    return None


def format_eta_label(minutes):
    if minutes <= 0:
        return 'Arriving now'
    hours, mins = divmod(minutes, 60)
    if hours:
        return f'~{hours} h {mins} min'
    return f'~{mins} min'


_eta_label = format_eta_label


def calculate_eta(route_stops, current_stop, next_stop, start_at=None):
    """ETA = segment distance / segment average speed, summed when skipping."""
    if current_stop is None or next_stop is None:
        return None
    if next_stop.sequence <= current_stop.sequence:
        return None

    total_distance = 0.0
    total_minutes = 0.0
    for stop in route_stops:
        if stop.sequence <= current_stop.sequence:
            continue
        if stop.sequence > next_stop.sequence:
            break
        distance = float(stop.distance_from_previous_km or 0)
        speed = int(stop.average_speed_kmh or 45)
        total_distance += distance
        if speed:
            total_minutes += (distance / speed) * 60

    if total_distance <= 0:
        return None

    minutes = max(0, int(round(total_minutes)))
    average_speed = int(round(total_distance / (total_minutes / 60))) if total_minutes else 45
    start_at = start_at or timezone.now()
    eta_at = start_at + timedelta(minutes=minutes)
    return {
        'distance_km': round(total_distance, 2),
        'average_speed_kmh': average_speed,
        'eta_minutes': minutes,
        'minutes': minutes,
        'eta_at': eta_at,
        'eta': eta_at,
        'eta_label': _eta_label(minutes),
    }


def route_eta_summary(bus, current_name, start_at=None):
    """Return the immediate next stop and final destination with separate ETAs."""
    route = find_route_for_bus(bus)
    if route is None:
        return None
    current_stop = find_stop(route, current_name)
    if current_stop is None:
        return None

    stops = list(route.stops.select_related('terminal').order_by('sequence'))
    later_stops = [stop for stop in stops if stop.sequence > current_stop.sequence]
    if not later_stops:
        return None

    next_stop = later_stops[0]
    final_stop = later_stops[-1]
    return {
        'route': route,
        'current_stop': current_stop,
        'next_stop': next_stop,
        'final_stop': final_stop,
        'next_eta': calculate_eta(stops, current_stop, next_stop, start_at),
        'final_eta': calculate_eta(stops, current_stop, final_stop, start_at),
    }


def build_stop_payload(route, current_stop):
    """Return all route stops plus the ETA for every valid next stop."""
    stops = list(route.stops.select_related('terminal').order_by('sequence'))
    if current_stop is None:
        return None

    all_stops = [
        {
            'name': stop.terminal.name,
            'sequence': stop.sequence,
            'is_current': stop.pk == current_stop.pk,
        }
        for stop in stops
    ]

    next_stops = []
    for stop in stops:
        if stop.sequence <= current_stop.sequence:
            continue
        eta = calculate_eta(stops, current_stop, stop)
        if eta is None:
            continue
        next_stops.append({
            'name': stop.terminal.name,
            'sequence': stop.sequence,
            'distance_km': eta['distance_km'],
            'average_speed_kmh': eta['average_speed_kmh'],
            'eta_minutes': eta['eta_minutes'],
            'eta_at': eta['eta_at'].isoformat(),
            'eta_label': eta['eta_label'],
        })

    return {
        'route': route,
        'current_stop': current_stop,
        'all_stops': all_stops,
        'next_stops': next_stops,
        'prompt': FIXED_CONDUCTOR_PROMPT,
        'validation_status': route.validation_status,
        'validation_note': route.validation_note,
    }


def record_next_stop(bus, route, current_stop, next_stop, user=None):
    """Log the conductor's next-stop choice and its computed ETA."""
    from .models import BusNextStopLog

    stops = list(route.stops.select_related('terminal').order_by('sequence'))
    eta = calculate_eta(stops, current_stop, next_stop)
    if eta is None:
        return None
    return BusNextStopLog.objects.create(
        bus=bus,
        route=route,
        current_station=current_stop.terminal,
        next_stop=next_stop.terminal,
        distance_km=eta['distance_km'],
        average_speed_kmh=eta['average_speed_kmh'],
        eta_minutes=eta['eta_minutes'],
        eta_at=eta['eta_at'],
        user=user if user and user.is_authenticated else None,
    )
