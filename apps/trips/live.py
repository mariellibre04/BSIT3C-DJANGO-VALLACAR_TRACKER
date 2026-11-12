"""Live trip rows derived from the current bus movement status.

Trips are normally recorded by hand, so the Trips page used to stay empty
even while buses were already running. These helpers turn an active bus and
its movement status into a read-only ``Trip`` instance so the page mirrors
the fleet in real time.

The rows are never saved. Admin-created ``Trip`` records stay the single
source of truth for editing, deleting, and reporting, and a bus that already
has an open trip is skipped so the same run is never listed twice.
"""

import re
from datetime import datetime, timedelta

from django.utils import timezone

from apps.bus.models import Bus
from apps.scoping import manageable_buses, scoped_trips

from .models import Trip

# Bus movement status -> trip status shown on the Trips page.
MOVEMENT_TO_TRIP_STATUS = {
    Bus.MOVE_AT_TERMINAL: Trip.STATUS_SCHEDULED,
    Bus.MOVE_EN_ROUTE: Trip.STATUS_EN_ROUTE,
    Bus.MOVE_STOPPED: Trip.STATUS_UNEXPECTED_STOP,
    Bus.MOVE_DELAYED: Trip.STATUS_DELAYED,
    Bus.MOVE_OFF_ROUTE: Trip.STATUS_REROUTED,
}

# Statuses that mean "this bus already has a run on the board".
OPEN_TRIP_STATUSES = [
    Trip.STATUS_SCHEDULED,
    Trip.STATUS_EN_ROUTE,
    Trip.STATUS_ON_TIME,
    Trip.STATUS_DELAYED,
    Trip.STATUS_REROUTED,
    Trip.STATUS_UNEXPECTED_STOP,
]

_ROUTE_SPLIT = re.compile(r'\s+(?:-|\u2013|\u2014|\u2192|>|to)\s+', re.IGNORECASE)


def route_endpoints(route):
    """Split ``Bacolod - Kabankalan`` without breaking ``Hinoba-an``."""
    parts = [part.strip() for part in _ROUTE_SPLIT.split(route or '') if part.strip()]
    if not parts:
        return '', ''
    if len(parts) == 1:
        return parts[0], ''
    return parts[0], parts[-1]


def _minutes_from_reason(reason):
    match = re.search(r'(\d+)\s*(?:min|minute)', reason or '', re.IGNORECASE)
    return int(match.group(1)) if match else 0


def _clock_datetime(day, clock):
    if clock is None:
        return None
    return timezone.make_aware(datetime.combine(day, clock))


def trip_status_for_bus(bus):
    return MOVEMENT_TO_TRIP_STATUS.get(bus.movement_status, Trip.STATUS_SCHEDULED)


def live_trip_for_bus(bus, now=None):
    """Build an unsaved Trip row for one active bus."""
    now = now or timezone.now()
    day = timezone.localdate(now)
    route_origin, route_destination = route_endpoints(bus.route)

    origin = (
        (bus.current_terminal or '').strip()
        or route_origin
        or (bus.route or '').strip()
        or 'Terminal'
    )
    destination = (
        (bus.final_destination or '').strip()
        or (bus.next_terminal or '').strip()
        or route_destination
        or (bus.route or '').strip()
        or origin
    )

    departure_clock = bus.scheduled_time or bus.actual_departure
    if departure_clock is None and bus.last_gps_update:
        departure_clock = timezone.localtime(bus.last_gps_update).time()
    if departure_clock is None:
        departure_clock = timezone.localtime(now).time().replace(second=0, microsecond=0)

    arrival_clock = bus.final_destination_eta or bus.next_terminal_eta
    if arrival_clock is not None and arrival_clock <= departure_clock:
        arrival_clock = None

    departure = _clock_datetime(day, departure_clock)
    arrival = _clock_datetime(day, arrival_clock) or departure + timedelta(hours=2)

    status = trip_status_for_bus(bus)
    reason = (bus.movement_reason or '').strip()

    return Trip(
        bus=bus,
        origin=origin,
        destination=destination,
        route=bus.route or f'{origin} - {destination}',
        scheduled_departure=departure,
        scheduled_arrival=arrival,
        status=status,
        delay_minutes=_minutes_from_reason(reason) if status == Trip.STATUS_DELAYED else 0,
        passenger_count=0,
        notes=reason or f'Live bus status: {bus.get_movement_status_display()}',
    )


def live_trips(user, now=None):
    """Read-only trip rows for every active bus without an open saved trip."""
    now = now or timezone.now()
    open_bus_ids = set(
        scoped_trips(user).filter(
            bus__isnull=False,
            status__in=OPEN_TRIP_STATUSES,
        ).values_list('bus_id', flat=True)
    )
    buses = manageable_buses(user).filter(status=Bus.STATUS_ACTIVE).exclude(
        pk__in=open_bus_ids
    ).order_by('bus_number')
    return [live_trip_for_bus(bus, now=now) for bus in buses]


def matches_query(trip, needle):
    """Case-insensitive search across the fields the Trips search box covers."""
    if not needle:
        return True
    needle = needle.lower()
    haystack = ' '.join(
        filter(None, [
            trip.bus.bus_number if trip.bus else '',
            trip.origin,
            trip.destination,
            trip.route,
        ])
    ).lower()
    return needle in haystack
