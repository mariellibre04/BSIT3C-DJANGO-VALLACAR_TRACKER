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

    def test_inactive_bus_is_left_off_the_board(self):
        self.bus.status = Bus.STATUS_INACTIVE
        self.bus.save(update_fields=['status', 'updated_at'])

        data = self.client.get(reverse('bus:bus_kiosk_refresh')).json()

        self.assertNotIn('101', data['board_html'])
