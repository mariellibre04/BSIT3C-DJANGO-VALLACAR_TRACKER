import json

from django.test import TestCase
from django.urls import reverse

from .models import Bus, BusTerminalTap


class TerminalScanTests(TestCase):
    def setUp(self):
        self.bus = Bus.objects.create(
            bus_number='101',
            plate_number='ABC-101',
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


class KioskRefreshTests(TestCase):
    def setUp(self):
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
        self.assertIn('Now at terminal', data['board_html'])
        self.assertIn('101', data['board_html'])
        self.assertIn('<strong>1</strong> at terminal', data['terminals_html'])

    def test_kiosk_page_renders_live_board_and_refresh_hook(self):
        response = self.client.get(reverse('bus:bus_kiosk'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '101')
        self.assertContains(response, 'id="kioskTableWrap"')
        self.assertContains(response, 'id="kioskTerminals"')
        self.assertContains(response, reverse('bus:bus_kiosk_refresh'))

    def test_inactive_bus_is_left_off_the_board(self):
        self.bus.status = Bus.STATUS_INACTIVE
        self.bus.save(update_fields=['status', 'updated_at'])

        data = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.assertNotIn('101', data['board_html'])

    def test_dedicated_terminal_kiosk_page_renders_negros_occidental_only(self):
        response = self.client.get(
            reverse('bus:bus_kiosk_terminal', args=['bacolod-north'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bacolod North Bus Terminal')
        self.assertContains(response, 'id="kioskSidebarList"')
        self.assertContains(response, 'Negros Occidental')
        self.assertNotContains(response, 'Cebu South Bus Terminal')
        self.assertNotContains(response, 'PITX')

    def test_terminal_kiosk_filters_board_to_that_terminal(self):
        other = Bus.objects.create(
            bus_number='202',
            plate_number='ABC-202',
            capacity=49,
            route='Mabinay - Dumaguete',
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

    def test_unknown_terminal_kiosk_redirects_to_all_terminals(self):
        response = self.client.get(
            reverse('bus:bus_kiosk_terminal', args=['not-a-real-terminal'])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('bus:bus_kiosk'))


class TerminalKioskQrTests(TestCase):
    def setUp(self):
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
        self.bus = Bus.objects.create(
            bus_number='909',
            plate_number='CEB-909',
            capacity=54,
            route='Cebu - Oslob',
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
                'terminal_id': 'CEBU-SOUTH',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.movement_status, Bus.MOVE_AT_TERMINAL)
        self.assertEqual(self.bus.current_location, 'CEBU-SOUTH Terminal')
        self.assertEqual(BusTerminalTap.objects.filter(bus=self.bus).count(), 1)
        self.assertEqual(response.json()['type'], 'IN')

    def test_api_scan_updates_terminal_monitor_feed(self):
        before = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': str(self.bus.qr_token),
                'type': 'IN',
                'terminal_id': 'CEBU-SOUTH',
            }),
            content_type='application/json',
        )
        after = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.assertNotEqual(before['version'], after['version'])
        self.assertIn('909', after['board_html'])
        self.assertIn('CEBU-SOUTH', after['board_html'])

    def test_api_checkout_marks_bus_en_route(self):
        response = self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': f'https://example.test/bus/tap/{self.bus.qr_token}/',
                'type': 'OUT',
                'terminal_id': 'CEBU-SOUTH',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.bus.refresh_from_db()
        self.assertEqual(self.bus.movement_status, Bus.MOVE_EN_ROUTE)
        self.assertEqual(self.bus.current_location, 'En route from CEBU-SOUTH Terminal')

    def test_api_checkout_also_appears_on_terminal_monitor_feed(self):
        before = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': str(self.bus.qr_token),
                'type': 'OUT',
                'terminal_id': 'CEBU-SOUTH',
            }),
            content_type='application/json',
        )
        after = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.assertNotEqual(before['version'], after['version'])
        self.assertIn('909', after['board_html'])
        self.assertIn('En Route', after['board_html'])
        self.assertIn('CEBU-SOUTH', after['board_html'])
        self.assertIn('909', after['ticker_html'])

    def test_api_rejects_invalid_type(self):
        response = self.client.post(
            reverse('terminal_checkin_api'),
            data=json.dumps({
                'bus_id': str(self.bus.qr_token),
                'type': 'MAYBE',
                'terminal_id': 'CEBU-SOUTH',
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
                'terminal_id': 'CEBU-SOUTH',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(BusTerminalTap.objects.exists())
