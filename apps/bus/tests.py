import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.roles import ROLE_ADMIN, ROLE_CONDUCTOR, set_role

from .models import (
    Bus,
    BusNextStopLog,
    BusStop,
    BusTerminalTap,
    DemoSeedState,
    Route,
    Terminal,
)
from .route_config import ROUTE_DEFINITIONS, TERMINAL_MASTER_LIST
from .route_service import INVALID_STOP_MESSAGE, seed_transit_data
from .views import DEMO_SEED_KEY, seed_static_demo_data


def make_conductor(username='conductor'):
    user = get_user_model().objects.create_user(
        username=username, password='secret1234'
    )
    set_role(user, ROLE_CONDUCTOR)
    return user


def make_admin(username='admin'):
    user = get_user_model().objects.create_user(
        username=username, password='secret1234'
    )
    set_role(user, ROLE_ADMIN)
    return user


class TerminalScanTests(TestCase):
    def setUp(self):
        self.client.force_login(make_conductor())
        self.bus = Bus.objects.create(
            bus_number='9001',
            plate_number='ABC-9001',
            capacity=50,
            route='Bacolod - Kabankalan',
            movement_status=Bus.MOVE_EN_ROUTE,
        )

    def test_valid_scan_checks_bus_in_at_terminal(self):
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Bacolod'},
        )

        self.assertEqual(response.status_code, 200)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.movement_status, Bus.MOVE_AT_TERMINAL)
        self.assertEqual(self.bus.current_location, 'Bacolod Terminal')
        self.assertEqual(BusTerminalTap.objects.filter(bus=self.bus).count(), 1)

    def test_scan_accepts_token_embedded_in_url(self):
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {
                'token': f'https://example.test/bus/tap/{self.bus.qr_token}/',
                'terminal': 'Bacolod',
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_scan_accepts_compact_token_without_dashes(self):
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {
                'token': f'https://example.test/bus/tap/{self.bus.qr_token.hex}/',
                'terminal': 'Bacolod',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(BusTerminalTap.objects.filter(bus=self.bus).exists())

    def test_scan_accepts_plain_payload_from_qr_reader(self):
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': self.bus.bus_number, 'terminal': 'Bacolod'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(BusTerminalTap.objects.filter(bus=self.bus).exists())

    def test_scan_page_does_not_use_native_barcode_detector(self):
        response = self.client.get(reverse('bus:bus_scan'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'useBarCodeDetectorIfSupported')
        self.assertContains(response, 'handleScanMiss')

    def test_invalid_token_is_rejected(self):
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': 'not-a-bus-token', 'terminal': 'Bacolod'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(BusTerminalTap.objects.exists())

    def test_unknown_terminal_is_rejected(self):
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Atlantis'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(BusTerminalTap.objects.exists())

    def test_scan_page_is_camera_only(self):
        response = self.client.get(reverse('bus:bus_scan'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'scanner_reader')
        self.assertContains(response, 'startWithCamera')
        self.assertNotContains(response, 'qr_upload')
        self.assertNotContains(response, 'scanFile')

    def test_scan_page_terminal_selection_is_optional(self):
        response = self.client.get(reverse('bus:bus_scan'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1. Terminal (optional)')
        self.assertContains(response, 'Choose next terminal stop')
        self.assertNotContains(response, 'Choose the terminal first')

    def test_scan_without_terminal_uses_bus_next_stop(self):
        self.bus.next_stop = 'Bago'
        self.bus.save(update_fields=['next_stop'])

        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['place'], 'Bago')
        self.assertTrue(
            BusTerminalTap.objects.filter(
                bus=self.bus, terminal_name='Bago', left_at__isnull=True
            ).exists()
        )

    def test_scan_without_terminal_falls_back_to_current_terminal(self):
        self.bus.current_terminal = 'Kabankalan'
        self.bus.save(update_fields=['current_terminal'])

        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['place'], 'Kabankalan')

    def test_rescan_without_terminal_times_out_at_inferred_terminal(self):
        self.bus.next_stop = 'Bago'
        self.bus.save(update_fields=['next_stop'])
        self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token)},
        )

        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'action': 'time_out'},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'time_out')
        self.assertEqual(data['place'], 'Bago')

    def test_scan_page_has_tolerant_jsqr_decoder(self):
        response = self.client.get(reverse('bus:bus_scan'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'jsqr.min.js')
        self.assertContains(response, 'startJsQrFallback')
        self.assertContains(response, 'decodeJsQrRegion')

    def test_scan_page_offers_manual_bus_entry(self):
        response = self.client.get(reverse('bus:bus_scan'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'manual_bus')
        self.assertContains(response, 'manual_tap')


class BusQrCodeTests(TestCase):
    """Bus QR codes must render large, with a quiet zone, so they scan."""

    def setUp(self):
        self.client.force_login(make_admin())

    def test_bus_list_builds_qr_with_quiet_zone(self):
        response = self.client.get(reverse('bus:bus_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'buildQrCanvas')
        self.assertContains(response, 'buildQrCanvas(qrUrl, 640)')


class KioskRefreshTests(TestCase):
    def setUp(self):
        self.client.force_login(make_conductor())
        self.bus = Bus.objects.create(
            bus_number='101',
            plate_number='ABC-101',
            capacity=50,
            route='Bacolod - Kabankalan',
            movement_status=Bus.MOVE_EN_ROUTE,
        )

    def test_refresh_returns_fragments_and_version(self):
        response = self.client.get(reverse('bus:bus_kiosk_refresh'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        for key in ('version', 'updated', 'buses', 'terminals_html', 'board_html', 'ticker_html'):
            self.assertIn(key, data)
        self.assertIn('101', data['board_html'])

    def test_version_is_stable_without_changes(self):
        first = self.client.get(reverse('bus:bus_kiosk_refresh')).json()['version']
        second = self.client.get(reverse('bus:bus_kiosk_refresh')).json()['version']

        self.assertEqual(first, second)

    def test_check_in_moves_bus_to_terminal_and_changes_version(self):
        before = self.client.get(reverse('bus:bus_kiosk_refresh')).json()['version']

        self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Bacolod'},
        )
        data = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.assertNotEqual(before, data['version'])
        self.assertIn('All buses', data['board_html'])
        self.assertIn('101', data['board_html'])
        self.assertIn('<strong>1</strong> at terminal', data['terminals_html'])

    def test_kiosk_page_renders_live_board_and_refresh_hook(self):
        response = self.client.get(reverse('bus:bus_kiosk'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '101')
        self.assertContains(response, 'id="kioskTableWrap"')
        self.assertNotContains(response, 'id="kioskTerminals"')
        self.assertContains(response, reverse('bus:bus_kiosk_refresh'))
        self.assertNotContains(response, 'Seats')
        self.assertNotContains(response, 'k-qr-btn')

    def test_kiosk_area_filter_shows_pass_through_eta(self):
        self.client.get(reverse('bus:bus_kiosk'))
        data = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?area=kabankalan'
        ).json()

        self.assertIn('102', data['board_html'])
        self.assertIn('Bacolod &rarr; Sipalay', data['board_html'])
        self.assertIn('Passes Kabankalan', data['board_html'])
        self.assertIn('ETA', data['board_html'])

    def test_kiosk_area_filter_keeps_relevant_buses(self):
        Bus.objects.create(
            bus_number='202',
            plate_number='ABC-202',
            capacity=49,
            route='Sipalay - Kabankalan',
            movement_status=Bus.MOVE_EN_ROUTE,
        )

        kabankalan = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?area=kabankalan'
        ).json()
        self.assertIn('101', kabankalan['board_html'])
        self.assertIn('202', kabankalan['board_html'])

        sipalay = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?area=sipalay'
        ).json()
        self.assertIn('202', sipalay['board_html'])
        self.assertNotIn('101', sipalay['board_html'])
        self.assertIn('Kabankalan', sipalay['board_html'])

    def test_inactive_bus_is_left_off_the_board(self):
        self.bus.status = Bus.STATUS_INACTIVE
        self.bus.save(update_fields=['status', 'updated_at'])

        data = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.assertNotIn('101', data['board_html'])

    def test_dedicated_terminal_kiosk_lists_negros_occidental_terminals(self):
        response = self.client.get(
            reverse('bus:bus_kiosk_terminal', args=['bacolod-north'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bacolod North Bus Terminal')
        self.assertContains(response, 'id="kioskSidebarList"')
        self.assertContains(response, 'Negros Occidental')
        self.assertContains(response, 'Kabankalan Bus Terminal')
        self.assertNotContains(response, 'Cebu South Bus Terminal')
        self.assertNotContains(response, 'PITX')

    def test_terminal_kiosk_filters_board_to_that_terminal(self):
        other = Bus.objects.create(
            bus_number='202',
            plate_number='ABC-202',
            capacity=49,
            route='Sipalay - Kabankalan',
            movement_status=Bus.MOVE_EN_ROUTE,
        )
        self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Bacolod'},
        )
        self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(other.qr_token), 'terminal': 'San Carlos'},
        )

        data = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?terminal=bacolod-north'
        ).json()

        self.assertEqual(data['selected'], 'bacolod-north')
        self.assertIn('101', data['board_html'])
        self.assertNotIn('202', data['board_html'])
        self.assertIn('Bacolod', data['sidebar_html'])

    def test_terminal_kiosk_shows_only_the_selected_terminal_card(self):
        response = self.client.get(
            reverse('bus:bus_kiosk_terminal', args=['kabankalan'])
        )

        self.assertEqual(
            [card['slug'] for card in response.context['kiosk_terminals']],
            ['kabankalan'],
        )

    def test_terminal_kiosk_assigns_static_bays(self):
        response = self.client.get(
            reverse('bus:bus_kiosk_terminal', args=['kabankalan'])
        )

        rows = response.context['kiosk_inbound'] + response.context['kiosk_at_terminal']
        bus = next(row for row in rows if row['number'] == '106')
        self.assertEqual(bus['bay'], 'Bay 06')

    def test_unknown_terminal_kiosk_redirects_to_all_terminals(self):
        response = self.client.get(
            reverse('bus:bus_kiosk_terminal', args=['not-a-real-terminal'])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('bus:bus_kiosk'))


class TerminalKioskQrTests(TestCase):
    def setUp(self):
        self.client.force_login(make_conductor())
        self.bus = Bus.objects.create(
            bus_number='101',
            plate_number='ABC-101',
            capacity=50,
            route='Bacolod - Kabankalan',
            movement_status=Bus.MOVE_EN_ROUTE,
        )

    def test_kiosk_qr_is_locked_to_selected_terminal(self):
        response = self.client.get(
            reverse('bus:bus_kiosk_terminal', args=['kabankalan'])
        )

        qr_data = response.context['kiosk_qr_data']
        self.assertTrue(qr_data['auto'])
        self.assertEqual(qr_data['terminal_slug'], 'kabankalan')
        self.assertIn('terminal=kabankalan', qr_data['buses']['101'])
        self.assertIn('auto=1', qr_data['buses']['101'])
        self.assertIn('terminal=kabankalan', qr_data['scan'])

    def test_locked_bus_qr_times_in_then_out_automatically(self):
        url = reverse('bus:bus_tap', args=[str(self.bus.qr_token)])

        response = self.client.get(url, {'terminal': 'kabankalan', 'auto': '1'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('done=1', response['Location'])
        tap = BusTerminalTap.objects.get(bus=self.bus)
        self.assertEqual(tap.terminal_name, 'Kabankalan')
        self.assertIsNone(tap.left_at)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.movement_status, Bus.MOVE_AT_TERMINAL)

        self.client.get(url, {'terminal': 'kabankalan', 'auto': '1'})

        tap.refresh_from_db()
        self.assertIsNotNone(tap.left_at)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.movement_status, Bus.MOVE_EN_ROUTE)

    def test_scan_at_new_terminal_closes_previous_stop(self):
        url = reverse('bus:bus_tap', args=[str(self.bus.qr_token)])

        self.client.get(url, {'terminal': 'kabankalan', 'auto': '1'})
        self.client.get(url, {'terminal': 'victorias', 'auto': '1'})

        self.assertEqual(BusTerminalTap.objects.filter(bus=self.bus).count(), 2)
        first = BusTerminalTap.objects.get(bus=self.bus, terminal_name='Kabankalan')
        latest = BusTerminalTap.objects.get(bus=self.bus, terminal_name='Victorias')
        self.assertIsNotNone(first.left_at)
        self.assertIsNone(latest.left_at)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.current_location, 'Victorias Terminal')

    def test_locked_tap_page_shows_the_next_automatic_action(self):
        url = reverse('bus:bus_tap', args=[str(self.bus.qr_token)])

        page = self.client.get(url, {'terminal': 'kabankalan'})

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Automatic tap')
        self.assertContains(page, 'Time In at Kabankalan')
        self.assertNotContains(page, 'id="tap_terminal"')

    def test_locked_manual_checkin_automatically_times_in(self):
        url = reverse('bus:conductor_checkin') + '?terminal=kabankalan'
        page = self.client.get(url)
        self.assertContains(page, 'Locked to Kabankalan Bus Terminal')

        response = self.client.post(url, {'bus': self.bus.id})

        self.assertEqual(response.status_code, 302)
        tap = BusTerminalTap.objects.get(bus=self.bus)
        self.assertEqual(tap.terminal_name, 'Kabankalan')
        self.assertIsNone(tap.left_at)

    def test_refresh_keeps_bus_qrs_locked_to_terminal(self):
        data = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?terminal=kabankalan'
        ).json()

        self.assertIn('terminal=kabankalan', data['buses']['101'])
        self.assertIn('auto=1', data['buses']['101'])

    def test_scan_page_locks_selected_terminal(self):
        response = self.client.get(reverse('bus:bus_scan') + '?terminal=kabankalan')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Locked to Kabankalan Bus Terminal')
        self.assertContains(response, 'value="Kabankalan Bus Terminal" selected')
        self.assertNotContains(response, 'id="terminal_combobox"')


class TerminalStaffScannerTests(TestCase):
    def setUp(self):
        self.client.force_login(make_conductor())
        self.bus = Bus.objects.create(
            bus_number='909',
            plate_number='BCD-909',
            capacity=54,
            route='Bacolod - Kabankalan',
            movement_status=Bus.MOVE_EN_ROUTE,
        )

    def test_terminal_scan_page_renders_mobile_scanner(self):
        response = self.client.get(reverse('terminal_scan'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SCAN BUS QR')
        self.assertContains(response, 'BUS ARRIVED (IN)')
        self.assertContains(response, 'BUS LEFT (OUT)')
        self.assertContains(response, 'html5-qrcode')
        self.assertContains(response, 'terminal-bus.svg')

    def test_api_checkin_records_arrival(self):
        response = self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': str(self.bus.qr_token),
                'type': 'IN',
                'terminal_id': 'BACOLOD-SOUTH',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.movement_status, Bus.MOVE_AT_TERMINAL)
        self.assertEqual(self.bus.current_location, 'Bacolod South Terminal')
        self.assertEqual(BusTerminalTap.objects.filter(bus=self.bus).count(), 1)
        self.assertEqual(response.json()['type'], 'IN')

    def test_api_scan_updates_terminal_monitor_feed(self):
        before = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?area=bacolod-south'
        ).json()

        self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': str(self.bus.qr_token),
                'type': 'IN',
                'terminal_id': 'BACOLOD-SOUTH',
            }),
            content_type='application/json',
        )
        after = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?area=bacolod-south'
        ).json()

        self.assertNotEqual(before['version'], after['version'])
        self.assertIn('909', after['board_html'])
        self.assertIn('Bacolod South', after['board_html'])

    def test_api_checkout_marks_bus_en_route(self):
        response = self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': f'https://example.test/bus/tap/{self.bus.qr_token}/',
                'type': 'OUT',
                'terminal_id': 'BACOLOD-SOUTH',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.movement_status, Bus.MOVE_EN_ROUTE)
        self.assertEqual(self.bus.current_location, 'En route from Bacolod South Terminal')

    def test_api_checkout_also_appears_on_terminal_monitor_feed(self):
        before = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?area=bacolod-south'
        ).json()

        self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': str(self.bus.qr_token),
                'type': 'OUT',
                'terminal_id': 'BACOLOD-SOUTH',
            }),
            content_type='application/json',
        )
        after = self.client.get(
            reverse('bus:bus_kiosk_refresh') + '?area=bacolod-south'
        ).json()

        self.assertNotEqual(before['version'], after['version'])
        self.assertIn('909', after['board_html'])
        self.assertIn('En Route', after['board_html'])
        self.assertIn('Bacolod South', after['board_html'])
        self.assertIn('909', after['ticker_html'])

    def test_api_rejects_invalid_type(self):
        response = self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': str(self.bus.qr_token),
                'type': 'MAYBE',
                'terminal_id': 'BACOLOD-SOUTH',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(BusTerminalTap.objects.exists())

    def test_api_rejects_unknown_bus(self):
        response = self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': 'not-a-bus',
                'type': 'IN',
                'terminal_id': 'BACOLOD-SOUTH',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(BusTerminalTap.objects.exists())


class RouteNextStopTests(TestCase):
    def setUp(self):
        self.client.force_login(make_conductor())
        seed_transit_data(force=True)
        self.bus = Bus.objects.create(
            bus_number='KDM-900',
            plate_number='VTI 9900',
            capacity=49,
            route='Kabankalan-Bacolod',
            movement_status=Bus.MOVE_EN_ROUTE,
        )

    def test_seed_creates_every_master_list_terminal_and_route(self):
        self.assertEqual(Terminal.objects.count(), len(TERMINAL_MASTER_LIST))
        self.assertEqual(Route.objects.count(), len(ROUTE_DEFINITIONS))

    def test_route_stops_only_returns_stops_after_current(self):
        response = self.client.get(
            reverse('bus:bus_route_stops_ajax'),
            {'token': str(self.bus.qr_token), 'current': 'Kabankalan'},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['current_station'], 'Kabankalan')
        self.assertEqual(
            data['current_station_label'], 'Current Bus Station: Kabankalan.'
        )
        self.assertEqual(
            [stop['name'] for stop in data['next_stops']],
            [
                'Himamaylan', 'Binalbagan', 'Hinigaran', 'Pontevedra',
                'Valladolid', 'Bago', 'Bacolod South',
            ],
        )
        self.assertTrue(all(stop['eta_minutes'] > 0 for stop in data['next_stops']))

    def test_route_stops_rejects_stop_not_on_route(self):
        response = self.client.get(
            reverse('bus:bus_route_stops_ajax'),
            {'token': str(self.bus.qr_token), 'current': 'Sipalay'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], INVALID_STOP_MESSAGE)

    def test_next_stop_logs_distance_speed_and_eta(self):
        response = self.client.post(
            reverse('bus:bus_next_stop_ajax'),
            {
                'token': str(self.bus.qr_token),
                'current': 'Kabankalan',
                'next_stop': 'Himamaylan',
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['next_stop'], 'Himamaylan')
        self.assertAlmostEqual(float(data['distance_km']), 19.0, places=2)
        self.assertGreater(data['eta_minutes'], 0)
        self.assertEqual(data['final_destination'], 'Bacolod South')
        self.assertIsNotNone(data['final_destination_eta'])
        self.assertGreater(
            data['final_destination_eta_minutes'], data['eta_minutes']
        )
        log = BusNextStopLog.objects.get(bus=self.bus)
        self.assertEqual(log.current_station.name, 'Kabankalan')
        self.assertEqual(log.next_stop.name, 'Himamaylan')
        self.assertAlmostEqual(float(log.distance_km), 19.0, places=2)

    def test_confirmed_next_stop_is_shown_on_the_kiosk(self):
        response = self.client.post(
            reverse('bus:bus_next_stop_ajax'),
            {
                'token': str(self.bus.qr_token),
                'current': 'Kabankalan',
                'next_stop': 'Himamaylan',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.next_stop, 'Himamaylan')
        self.assertIsNotNone(self.bus.next_stop_eta)
        self.assertEqual(self.bus.final_destination, 'Bacolod South')
        board = self.client.get(reverse('bus:bus_kiosk_refresh')).json()['board_html']
        self.assertIn('Next terminal stop: Himamaylan', board)
        self.assertIn('Final: Bacolod South', board)

    def test_next_stop_rejects_stop_before_current(self):
        response = self.client.post(
            reverse('bus:bus_next_stop_ajax'),
            {
                'token': str(self.bus.qr_token),
                'current': 'Bago',
                'next_stop': 'Himamaylan',
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], INVALID_STOP_MESSAGE)
        self.assertFalse(BusNextStopLog.objects.exists())

    def test_time_out_records_selected_next_stop(self):
        self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Kabankalan'},
        )
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {
                'token': str(self.bus.qr_token),
                'terminal': 'Kabankalan',
                'action': 'time_out',
                'next_stop': 'Himamaylan',
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['selected_next_stop'], 'Himamaylan')
        self.assertIsNotNone(data['next_stop_eta_at'])
        log = BusNextStopLog.objects.get(bus=self.bus)
        self.assertEqual(log.next_stop.name, 'Himamaylan')

        self.bus.refresh_from_db()
        self.assertEqual(self.bus.next_stop, 'Himamaylan')
        self.assertIsNotNone(self.bus.next_stop_eta)
        self.assertEqual(self.bus.final_destination, 'Bacolod South')
        board = self.client.get(reverse('bus:bus_kiosk_refresh')).json()['board_html']
        self.assertIn('Next terminal stop: Himamaylan', board)

    def test_time_out_rejects_invalid_next_stop(self):
        self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Kabankalan'},
        )
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {
                'token': str(self.bus.qr_token),
                'terminal': 'Kabankalan',
                'action': 'time_out',
                'next_stop': 'Sipalay',
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], INVALID_STOP_MESSAGE)
        self.assertFalse(BusNextStopLog.objects.exists())
        tap = BusTerminalTap.objects.get(bus=self.bus)
        self.assertIsNone(tap.left_at)

    def test_time_in_payload_includes_current_station_label_and_next_stops(self):
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Kabankalan'},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data['current_station_label'], 'Current Bus Station: Kabankalan.'
        )
        self.assertEqual(
            [stop['name'] for stop in data['next_stops']],
            [
                'Himamaylan', 'Binalbagan', 'Hinigaran', 'Pontevedra',
                'Valladolid', 'Bago', 'Bacolod South',
            ],
        )

    def test_scan_payload_has_different_next_stop_and_final_destination_etas(self):
        response = self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Kabankalan'},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['next_stop'], 'Himamaylan')
        self.assertEqual(data['final_destination'], 'Bacolod South')
        self.assertIsNotNone(data['next_stop_eta'])
        self.assertIsNotNone(data['final_destination_eta'])
        self.assertLess(
            data['next_stop_eta_minutes'],
            data['final_destination_eta_minutes'],
        )

    def test_kiosk_shows_next_stop_and_final_destination_etas(self):
        self.client.post(
            reverse('bus:bus_scan_checkin_ajax'),
            {'token': str(self.bus.qr_token), 'terminal': 'Kabankalan'},
        )
        data = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.assertIn('Next terminal stop Himamaylan ETA', data['ticker_html'])
        self.assertIn('Final Bacolod South ETA', data['ticker_html'])
        self.assertIn('Next terminal stop: Himamaylan', data['board_html'])
        self.assertIn('Final: Bacolod South', data['board_html'])

class AdminKioskSyncTests(TestCase):
    def setUp(self):
        self.client.force_login(make_admin())
        seed_static_demo_data()

    def test_admin_bus_list_reads_the_kiosk_fleet(self):
        response = self.client.get(reverse('bus:bus_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '101')
        self.assertEqual(
            response.context['buses'].paginator.count, Bus.objects.count()
        )

    def test_admin_dashboard_counts_match_kiosk_buses(self):
        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_buses'], Bus.objects.count())

    def test_admin_edit_is_reflected_on_kiosk(self):
        bus = Bus.objects.get(bus_number='101')
        response = self.client.post(
            reverse('bus:bus_save_ajax'),
            {
                'id': bus.id,
                'bus_number': bus.bus_number,
                'plate_number': bus.plate_number,
                'capacity': bus.capacity,
                'route': bus.route,
                'status': Bus.STATUS_ACTIVE,
                'movement_status': Bus.MOVE_EN_ROUTE,
                'current_terminal': 'Kabankalan',
                'bay': 'Bay 03',
                'next_stop': 'Candoni',
                'next_terminal': 'Candoni',
                'next_terminal_eta': '10:30',
                'final_destination': 'Candoni',
                'final_destination_eta': '11:45',
            },
        )

        self.assertEqual(response.status_code, 200)
        bus.refresh_from_db()
        self.assertEqual(bus.next_terminal, 'Candoni')
        self.assertEqual(bus.next_stop, 'Candoni')
        board = self.client.get(reverse('bus:bus_kiosk_refresh')).json()['board_html']
        self.assertIn('Candoni', board)

    def test_demo_seed_does_not_overwrite_admin_edits(self):
        bus = Bus.objects.get(bus_number='101')
        Bus.objects.filter(pk=bus.pk).update(
            plate_number='ADMIN-EDIT',
            capacity=30,
            route='Admin - Route',
            status=Bus.STATUS_MAINTENANCE,
            bay='Bay 07',
        )

        seed_static_demo_data(force=True)

        bus.refresh_from_db()
        self.assertEqual(bus.plate_number, 'ADMIN-EDIT')
        self.assertEqual(bus.capacity, 30)
        self.assertEqual(bus.route, 'Admin - Route')
        self.assertEqual(bus.status, Bus.STATUS_MAINTENANCE)
        self.assertEqual(bus.bay, 'Bay 07')

    def test_deleted_demo_bus_is_not_recreated(self):
        Bus.objects.get(bus_number='101').delete()

        seed_static_demo_data()

        self.assertFalse(Bus.objects.filter(bus_number='101').exists())
        self.assertTrue(DemoSeedState.objects.filter(key=DEMO_SEED_KEY).exists())


class BusFormRouteStopsTests(TestCase):
    """The next-stop picker must follow the stops of the chosen route."""

    def setUp(self):
        self.client.force_login(make_admin())
        seed_transit_data(force=True)

    def test_catalog_is_negros_occidental_only(self):
        response = self.client.get(reverse('bus:bus_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context['route_options']),
            {definition['name'] for definition in ROUTE_DEFINITIONS},
        )
        terminals = set(response.context['terminal_options'])
        self.assertTrue(terminals)
        for out_of_scope in (
            'Dumaguete', 'Bais', 'Mabinay', 'Tanjay', 'Sibulan',
            'Cebu South', 'Cebu North',
        ):
            self.assertNotIn(out_of_scope, terminals)

    def test_bus_list_exposes_route_stop_catalog(self):
        response = self.client.get(reverse('bus:bus_list'))

        self.assertEqual(response.status_code, 200)
        stops = response.context['route_stop_map']['Kabankalan-Bacolod']
        self.assertEqual(
            stops,
            [
                'Kabankalan',
                'Himamaylan',
                'Binalbagan',
                'Hinigaran',
                'Pontevedra',
                'Valladolid',
                'Bago',
                'Bacolod South',
            ],
        )
        # Aliases resolve to the same ordered stop list.
        self.assertEqual(
            response.context['route_stop_map']['Kabankalan - Bacolod'], stops
        )

    def test_save_rejects_next_stop_outside_the_route(self):
        response = self.client.post(
            reverse('bus:bus_save_ajax'),
            {
                'bus_number': 'KAB-901',
                'plate_number': 'VTI 9901',
                'capacity': 49,
                'route': 'Kabankalan - Bacolod',
                'next_stop': 'Dumaguete',
                'status': Bus.STATUS_ACTIVE,
                'movement_status': Bus.MOVE_AT_TERMINAL,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('selected route', response.json()['error'])
        self.assertFalse(Bus.objects.filter(bus_number='KAB-901').exists())

    def test_save_accepts_next_stop_on_the_route(self):
        response = self.client.post(
            reverse('bus:bus_save_ajax'),
            {
                'bus_number': 'KAB-902',
                'plate_number': 'VTI 9902',
                'capacity': 49,
                'route': 'Kabankalan - Bacolod',
                'current_terminal': 'Kabankalan',
                'next_stop': 'Bago',
                'final_destination': 'Bacolod South',
                'status': Bus.STATUS_ACTIVE,
                'movement_status': Bus.MOVE_EN_ROUTE,
            },
        )

        self.assertEqual(response.status_code, 200)
        bus = Bus.objects.get(bus_number='KAB-902')
        self.assertEqual(bus.next_stop, 'Bago')
        self.assertEqual(bus.final_destination, 'Bacolod South')

    def test_save_accepts_alias_stop_and_stores_canonical_name(self):
        response = self.client.post(
            reverse('bus:bus_save_ajax'),
            {
                'bus_number': 'KAB-903',
                'plate_number': 'VTI 9903',
                'capacity': 49,
                'route': 'Kabankalan-Bacolod',
                'next_stop': 'bacolod south',
                'status': Bus.STATUS_ACTIVE,
                'movement_status': Bus.MOVE_EN_ROUTE,
            },
        )

        self.assertEqual(response.status_code, 200)
        bus = Bus.objects.get(bus_number='KAB-903')
        self.assertEqual(bus.next_stop, 'Bacolod South')

    def test_save_stores_stop_sequence_with_etas(self):
        stops = [
            {'name': 'Kabankalan', 'eta': '08:00'},
            {'name': 'Himamaylan', 'eta': '08:25'},
            {'name': 'Binalbagan', 'eta': '08:40'},
            {'name': 'Hinigaran', 'eta': '08:52'},
            {'name': 'Bacolod South', 'eta': '09:30'},
        ]
        response = self.client.post(
            reverse('bus:bus_save_ajax'),
            {
                'bus_number': 'KAB-904',
                'plate_number': 'VTI 9904',
                'capacity': 49,
                'route': 'Kabankalan - Bacolod',
                'scheduled_time': '07:45',
                'status': Bus.STATUS_ACTIVE,
                'movement_status': Bus.MOVE_AT_TERMINAL,
                'stops_json': json.dumps(stops),
            },
        )

        self.assertEqual(response.status_code, 200)
        bus = Bus.objects.get(bus_number='KAB-904')
        saved = list(bus.assigned_stops.order_by('sequence'))
        self.assertEqual(
            [(stop.sequence, stop.name) for stop in saved],
            [
                (1, 'Kabankalan'),
                (2, 'Himamaylan'),
                (3, 'Binalbagan'),
                (4, 'Hinigaran'),
                (5, 'Bacolod South'),
            ],
        )
        self.assertEqual(saved[0].eta.strftime('%H:%M'), '08:00')
        self.assertEqual(saved[4].eta.strftime('%H:%M'), '09:30')
        # The first and last assigned stops fill the blank route fields.
        self.assertEqual(bus.next_stop, 'Kabankalan')
        self.assertEqual(bus.final_destination, 'Bacolod South')

    def test_stop_sequence_skips_current_terminal_for_next_stop(self):
        response = self.client.post(
            reverse('bus:bus_save_ajax'),
            {
                'bus_number': 'KAB-908',
                'plate_number': 'VTI 9908',
                'capacity': 49,
                'route': 'Kabankalan - Bacolod',
                'current_terminal': 'Kabankalan',
                'status': Bus.STATUS_ACTIVE,
                'movement_status': Bus.MOVE_AT_TERMINAL,
                'stops_json': json.dumps([
                    {'name': 'Kabankalan', 'eta': '08:00'},
                    {'name': 'Himamaylan', 'eta': '08:25'},
                    {'name': 'Bago', 'eta': '09:40'},
                ]),
            },
        )

        self.assertEqual(response.status_code, 200)
        bus = Bus.objects.get(bus_number='KAB-908')
        self.assertEqual(bus.next_stop, 'Himamaylan')
        self.assertEqual(bus.next_stop_eta.strftime('%H:%M'), '08:25')
        self.assertEqual(bus.final_destination, 'Bago')

    def test_save_rejects_stop_outside_the_route(self):
        response = self.client.post(
            reverse('bus:bus_save_ajax'),
            {
                'bus_number': 'KAB-905',
                'plate_number': 'VTI 9905',
                'capacity': 49,
                'route': 'Kabankalan - Bacolod',
                'status': Bus.STATUS_ACTIVE,
                'movement_status': Bus.MOVE_AT_TERMINAL,
                'stops_json': json.dumps([
                    {'name': 'Kabankalan', 'eta': '08:00'},
                    {'name': 'Dumaguete', 'eta': '09:00'},
                ]),
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('selected route', response.json()['error'])
        self.assertFalse(Bus.objects.filter(bus_number='KAB-905').exists())

    def test_edit_replaces_the_assigned_stop_sequence(self):
        bus = Bus.objects.create(
            bus_number='KAB-906',
            plate_number='VTI 9906',
            capacity=49,
            route='Kabankalan - Bacolod',
            status=Bus.STATUS_ACTIVE,
        )
        BusStop.objects.create(bus=bus, name='Kabankalan', sequence=1)

        response = self.client.post(
            reverse('bus:bus_save_ajax'),
            {
                'id': bus.id,
                'bus_number': bus.bus_number,
                'plate_number': bus.plate_number,
                'capacity': bus.capacity,
                'route': bus.route,
                'status': Bus.STATUS_ACTIVE,
                'movement_status': Bus.MOVE_AT_TERMINAL,
                'stops_json': json.dumps([
                    {'name': 'Himamaylan', 'eta': '09:00'},
                    {'name': 'Bago', 'eta': '10:15'},
                ]),
            },
        )

        self.assertEqual(response.status_code, 200)
        bus.refresh_from_db()
        self.assertEqual(
            [(stop.sequence, stop.name) for stop in bus.assigned_stops.all()],
            [(1, 'Himamaylan'), (2, 'Bago')],
        )

    def test_bus_list_exposes_assigned_stop_sequence_for_editing(self):
        bus = Bus.objects.create(
            bus_number='KAB-907',
            plate_number='VTI 9907',
            capacity=49,
            route='Kabankalan - Bacolod',
            status=Bus.STATUS_ACTIVE,
        )
        BusStop.objects.create(
            bus=bus, name='Kabankalan', sequence=1, eta='07:30'
        )

        response = self.client.get(reverse('bus:bus_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['bus_stops_map'][str(bus.id)],
            [{'name': 'Kabankalan', 'eta': '07:30'}],
        )
