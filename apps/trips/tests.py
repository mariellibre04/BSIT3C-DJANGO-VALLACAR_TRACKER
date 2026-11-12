from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.bus.models import Bus
from apps.core.roles import ROLE_ADMIN, set_role

from .live import live_trip_for_bus, live_trips, route_endpoints
from .models import Trip


def make_admin(username='admin'):
    user = get_user_model().objects.create_user(
        username=username, password='secret1234'
    )
    set_role(user, ROLE_ADMIN)
    return user


def make_bus(user, **overrides):
    data = {
        'bus_number': '101',
        'plate_number': 'ABC-101',
        'capacity': 50,
        'route': 'Kabankalan - Candoni',
        'status': Bus.STATUS_ACTIVE,
        'movement_status': Bus.MOVE_EN_ROUTE,
        'user': user,
    }
    data.update(overrides)
    return Bus.objects.create(**data)


class RouteEndpointTests(TestCase):
    def test_split_keeps_hyphenated_place_names(self):
        self.assertEqual(
            route_endpoints('Hinoba-an - Kabankalan'), ('Hinoba-an', 'Kabankalan')
        )

    def test_split_handles_arrow_and_single_endpoint(self):
        self.assertEqual(route_endpoints('Bacolod → Sipalay'), ('Bacolod', 'Sipalay'))
        self.assertEqual(route_endpoints('Bacolod'), ('Bacolod', ''))


class LiveTripTests(TestCase):
    def setUp(self):
        self.user = make_admin()
        self.now = timezone.now()

    def test_en_route_bus_becomes_live_trip(self):
        bus = make_bus(self.user)

        rows = live_trips(self.user)

        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0].pk)
        self.assertEqual(rows[0].bus, bus)
        self.assertEqual(rows[0].origin, 'Kabankalan')
        self.assertEqual(rows[0].destination, 'Candoni')
        self.assertEqual(rows[0].status, Trip.STATUS_EN_ROUTE)

    def test_movement_status_maps_to_trip_status(self):
        expected = {
            Bus.MOVE_AT_TERMINAL: Trip.STATUS_SCHEDULED,
            Bus.MOVE_EN_ROUTE: Trip.STATUS_EN_ROUTE,
            Bus.MOVE_STOPPED: Trip.STATUS_UNEXPECTED_STOP,
            Bus.MOVE_DELAYED: Trip.STATUS_DELAYED,
            Bus.MOVE_OFF_ROUTE: Trip.STATUS_REROUTED,
        }
        for index, (movement, status) in enumerate(expected.items()):
            bus = make_bus(
                self.user,
                bus_number=f'90{index}',
                plate_number=f'PLT-90{index}',
                movement_status=movement,
            )
            trip = live_trip_for_bus(bus, now=self.now)
            self.assertEqual(trip.status, status)

    def test_delay_minutes_read_from_movement_reason(self):
        bus = make_bus(
            self.user,
            movement_status=Bus.MOVE_DELAYED,
            movement_reason='Traffic buildup, 25 minutes late',
        )

        trip = live_trip_for_bus(bus, now=self.now)

        self.assertEqual(trip.delay_minutes, 25)

    def test_bus_with_open_trip_is_not_duplicated(self):
        bus = make_bus(self.user)
        Trip.objects.create(
            bus=bus,
            user=self.user,
            origin='Kabankalan',
            destination='Candoni',
            scheduled_departure=self.now,
            scheduled_arrival=self.now + timedelta(hours=2),
            status=Trip.STATUS_EN_ROUTE,
        )

        self.assertEqual(live_trips(self.user), [])

    def test_completed_trip_does_not_hide_live_run(self):
        bus = make_bus(self.user)
        Trip.objects.create(
            bus=bus,
            user=self.user,
            origin='Kabankalan',
            destination='Candoni',
            scheduled_departure=self.now - timedelta(hours=5),
            scheduled_arrival=self.now - timedelta(hours=3),
            status=Trip.STATUS_COMPLETED,
        )

        self.assertEqual(len(live_trips(self.user)), 1)

    def test_maintenance_bus_has_no_live_row(self):
        make_bus(self.user, status=Bus.STATUS_MAINTENANCE)

        self.assertEqual(live_trips(self.user), [])

    def test_unowned_kiosk_bus_is_shared_with_admin(self):
        Bus.objects.create(
            bus_number='201',
            plate_number='ABC-201',
            capacity=49,
            route='Bacolod - Sipalay',
            status=Bus.STATUS_ACTIVE,
            movement_status=Bus.MOVE_EN_ROUTE,
        )

        rows = live_trips(self.user)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].bus.bus_number, '201')


class TripListPageTests(TestCase):
    def setUp(self):
        self.user = make_admin()
        self.client.force_login(self.user)

    def test_page_lists_running_buses_even_without_saved_trips(self):
        make_bus(self.user, bus_number='101')

        response = self.client.get(reverse('trips:trip_list'))

        rows = list(response.context['trips'])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].bus.bus_number, '101')
        self.assertIsNone(rows[0].pk)
        self.assertContains(response, 'Kabankalan')

    def test_status_filter_matches_live_movement_status(self):
        make_bus(self.user, bus_number='101', movement_status=Bus.MOVE_EN_ROUTE)
        make_bus(
            self.user,
            bus_number='102',
            plate_number='ABC-102',
            movement_status=Bus.MOVE_DELAYED,
        )

        response = self.client.get(reverse('trips:trip_list'), {'status': 'delayed'})

        rows = list(response.context['trips'])
        self.assertEqual([row.bus.bus_number for row in rows], ['102'])
        self.assertEqual(rows[0].status, Trip.STATUS_DELAYED)

    def test_saved_open_trip_replaces_live_row(self):
        bus = make_bus(self.user, bus_number='101')
        Trip.objects.create(
            bus=bus,
            user=self.user,
            origin='Bacolod',
            destination='Sipalay',
            scheduled_departure=timezone.now(),
            scheduled_arrival=timezone.now() + timedelta(hours=3),
            status=Trip.STATUS_EN_ROUTE,
        )

        response = self.client.get(reverse('trips:trip_list'))

        rows = list(response.context['trips'])
        self.assertEqual(len(rows), 1)
        self.assertIsNotNone(rows[0].pk)

    def test_live_run_can_be_saved_for_unowned_kiosk_bus(self):
        bus = Bus.objects.create(
            bus_number='201',
            plate_number='ABC-201',
            capacity=49,
            route='Bacolod - Sipalay',
            status=Bus.STATUS_ACTIVE,
            movement_status=Bus.MOVE_EN_ROUTE,
        )

        response = self.client.post(reverse('trips:trip_save_ajax'), {
            'bus': bus.pk,
            'origin': 'Bacolod',
            'destination': 'Sipalay',
            'scheduled_departure': '2026-11-12T06:00',
            'scheduled_arrival': '2026-11-12T09:00',
            'status': Trip.STATUS_EN_ROUTE,
            'passenger_count': '0',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Trip.objects.filter(bus=bus, user=self.user).exists())
