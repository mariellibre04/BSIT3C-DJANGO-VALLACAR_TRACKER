from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .roles import ROLE_ADMIN, ROLE_CONDUCTOR, ROLE_PASSENGER, set_role


class DashboardViewTests(TestCase):
    def test_passenger_dashboard_is_public(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'passenger_dashboard.html')

    def test_admin_dashboard_requires_login(self):
        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_non_staff_cannot_reach_admin_dashboard(self):
        user = get_user_model().objects.create_user(username='passenger1', password='secret1234')

        self.client.force_login(user)
        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard'))

    def test_admin_dashboard_renders_for_staff(self):
        user = get_user_model().objects.create_user(
            username='dispatcher', password='secret1234', is_staff=True
        )

        self.client.force_login(user)
        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTrue(response.context['is_admin'])

    def test_welcome_page_renders(self):
        response = self.client.get(reverse('welcome'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'welcome.html')


class AdminAuthFlowTests(TestCase):
    def test_login_page_always_prompts_even_when_signed_in(self):
        user = get_user_model().objects.create_user(username='rider3', password='secret1234')

        self.client.force_login(user)
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_staff_login_redirects_to_admin_dashboard(self):
        get_user_model().objects.create_user(
            username='admin2', password='secret1234', is_staff=True
        )

        response = self.client.post(
            reverse('login'), {'username': 'admin2', 'password': 'secret1234'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('admin_dashboard'))

    def test_passenger_login_redirects_to_passenger_dashboard(self):
        get_user_model().objects.create_user(username='rider2', password='secret1234')

        response = self.client.post(
            reverse('login'), {'username': 'rider2', 'password': 'secret1234'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard'))

    def test_registration_creates_non_staff_and_goes_to_passenger_dashboard(self):
        response = self.client.post(reverse('register'), {
            'username': 'newrider',
            'first_name': 'New',
            'last_name': 'Rider',
            'email': 'newrider@example.com',
            'password': 'secret1234',
            'confirm_password': 'secret1234',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard'))
        self.assertFalse(get_user_model().objects.get(username='newrider').is_staff)


class LiveTrackingViewTests(TestCase):
    def test_bus_map_is_public(self):
        response = self.client.get(reverse('bus:bus_map'))

        self.assertEqual(response.status_code, 200)


class RoleSeparationTests(TestCase):
    def make_user(self, username, role=ROLE_PASSENGER):
        user = get_user_model().objects.create_user(
            username=username, password='secret1234'
        )
        set_role(user, role)
        return user

    def test_conductor_dashboard_requires_login(self):
        response = self.client.get(reverse('conductor_dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_conductor_login_redirects_to_conductor_dashboard(self):
        self.make_user('crew1', ROLE_CONDUCTOR)

        response = self.client.post(
            reverse('login'), {'username': 'crew1', 'password': 'secret1234'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('conductor_dashboard'))

    def test_conductor_dashboard_renders_scanner_and_monitor(self):
        user = self.make_user('crew2', ROLE_CONDUCTOR)
        self.client.force_login(user)

        response = self.client.get(reverse('conductor_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'conductor_dashboard.html')
        self.assertContains(response, reverse('bus:bus_scan'))
        self.assertContains(response, reverse('bus:bus_kiosk'))

    def test_conductor_cannot_reach_admin_dashboard(self):
        user = self.make_user('crew3', ROLE_CONDUCTOR)
        self.client.force_login(user)

        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('conductor_dashboard'))

    def test_conductor_can_scan_but_cannot_manage_fleet(self):
        user = self.make_user('crew4', ROLE_CONDUCTOR)
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse('bus:bus_scan')).status_code, 200)
        self.assertEqual(self.client.get(reverse('bus:bus_kiosk')).status_code, 200)

        response = self.client.get(reverse('bus:bus_list'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('conductor_dashboard'))

    def test_scanner_and_checkin_are_public_but_admin_pages_are_not(self):
        self.assertEqual(self.client.get(reverse('bus:bus_scan')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('bus:conductor_checkin')).status_code, 200
        )
        self.assertEqual(self.client.get(reverse('terminal_scan')).status_code, 200)

        user = self.make_user('rider9', ROLE_PASSENGER)
        self.client.force_login(user)

        response = self.client.get(reverse('users:user_list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard'))

    def test_admin_can_use_scanner_and_user_management(self):
        user = self.make_user('admin9', ROLE_ADMIN)
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse('bus:bus_scan')).status_code, 200)
        self.assertEqual(self.client.get(reverse('users:user_list')).status_code, 200)
