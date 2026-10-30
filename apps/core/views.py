from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .permissions import admin_required, conductor_required
from .roles import ROLE_ADMIN, ROLE_CONDUCTOR, get_role, landing_url_name

User = get_user_model()

MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION = timedelta(minutes=1)
INVALID_LOGIN_MESSAGE = 'Invalid username or password.'
LOCKED_MESSAGE = 'Too many failed attempts. Locked for 1 minute.'


def _reset_lock_state(request):
    request.session['failed_attempts'] = 0
    request.session['lock_time'] = None


def _get_lock_state(request):
    failed_attempts = request.session.get('failed_attempts', 0)
    lock_time = request.session.get('lock_time')

    if not lock_time:
        return failed_attempts, None

    try:
        unlock_time = timezone.datetime.fromisoformat(lock_time)
    except (TypeError, ValueError):
        _reset_lock_state(request)
        return 0, None

    if timezone.now() < unlock_time:
        remaining = int((unlock_time - timezone.now()).total_seconds())
        return failed_attempts, remaining

    _reset_lock_state(request)
    return 0, None


def _set_lock_state(request):
    lock_until = timezone.now() + LOCK_DURATION
    request.session['failed_attempts'] = MAX_FAILED_ATTEMPTS
    request.session['lock_time'] = lock_until.isoformat()
    return int(LOCK_DURATION.total_seconds())


def _validate_registration_data(data):
    errors = {}

    username = data.get('username', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not username:
        errors['username'] = 'Username is required.'
    elif User.objects.filter(username=username).exists():
        errors['username'] = 'Username already taken.'

    if not first_name:
        errors['first_name'] = 'First name is required.'

    if not last_name:
        errors['last_name'] = 'Last name is required.'

    if not email:
        errors['email'] = 'Email is required.'
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Enter a valid email address.'
        else:
            if User.objects.filter(email=email).exists():
                errors['email'] = 'Email already registered.'

    if not password:
        errors['password'] = 'Password is required.'
    elif len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters.'
    else:
        try:
            validate_password(password)
        except ValidationError as exc:
            errors['password'] = ' '.join(exc.messages)

    if password != confirm_password:
        errors['confirm_password'] = 'Passwords do not match.'

    return errors


@require_http_methods(['GET', 'POST'])
def login_view(request):
    failed_attempts, remaining = _get_lock_state(request)
    if remaining is not None:
        messages.error(request, f'Too many failed attempts. Try again in {remaining} seconds.')
        return render(request, 'auth/login.html', {'locked': True, 'remaining': remaining})

    if request.method == 'GET':
        return render(request, 'auth/login.html')

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        _reset_lock_state(request)
        login(request, user)
        role = get_role(user)
        if role == ROLE_ADMIN:
            messages.info(request, 'Signed in as an administrator.')
        elif role == ROLE_CONDUCTOR:
            messages.info(request, 'Signed in as a conductor.')
        else:
            messages.info(request, 'Signed in as a passenger.')
        return redirect(landing_url_name(role))

    failed_attempts += 1
    request.session['failed_attempts'] = failed_attempts
    if failed_attempts >= MAX_FAILED_ATTEMPTS:
        remaining = _set_lock_state(request)
        messages.error(request, LOCKED_MESSAGE)
        return render(request, 'auth/login.html', {'locked': True, 'remaining': remaining})

    remaining_attempts = MAX_FAILED_ATTEMPTS - failed_attempts
    messages.error(request, f'{INVALID_LOGIN_MESSAGE} {remaining_attempts} attempts remaining.')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('welcome')


def welcome_view(request):
    """Public landing: eye-catching passenger greeting with live fleet snapshot."""
    from django.db.models import Count, Sum
    from apps.bus.models import Bus

    buses = Bus.objects.annotate(total_passengers=Count('passengers', distinct=True))
    on_road = buses.filter(status=Bus.STATUS_ACTIVE).count()
    routes = buses.values('route').distinct().count()
    capacity = buses.aggregate(total=Sum('capacity'))['total'] or 0
    occupied = sum(b.total_passengers or 0 for b in buses)
    free_seats = max(0, capacity - occupied)

    from apps.bus.views import _kiosk_board_context, terminal_monitor_context
    context = terminal_monitor_context(request)
    context.update(_kiosk_board_context())
    context.update({
        'on_road': on_road,
        'free_seats': free_seats,
        'total_routes': routes,
    })
    return render(request, 'welcome.html', context)


def dashboard(request):
    """Passenger point of view (public).

    No login needed: riders see the live fleet, free seats and estimated
    arrivals, and can jump straight into the ETA board to plan a trip.
    """
    if request.user.is_authenticated and get_role(request.user) == ROLE_CONDUCTOR:
        return redirect('conductor_dashboard')

    from django.db.models import Count
    from apps.bus.models import Bus
    from apps.bus.views import (
        _bus_status_context, bus_map_coords, estimate_arrival, route_endpoints,
    )

    buses = list(
        Bus.objects.annotate(total_passengers=Count('passengers')).order_by('bus_number')
    )
    free_seats = 0
    on_road = 0
    for b in buses:
        occupied = b.total_passengers or 0
        b.seats_left = max(0, (b.capacity or 0) - occupied)
        b.occupancy_pct = int(round(occupied * 100.0 / b.capacity)) if b.capacity else 0
        b.display_location = b.current_location or b.route
        free_seats += b.seats_left
        if b.status == Bus.STATUS_ACTIVE:
            on_road += 1
        lat, lng, b.is_approx = bus_map_coords(b)
        _frm, _to = route_endpoints(b.route)
        dest = _to or _frm
        b.route_from, b.route_to = _frm, _to
        b.eta = estimate_arrival(lat, lng, dest['lat'], dest['lng'], b.movement_status) if dest else None
        b.eta_dest = dest['name'] if dest else ''
        _trip, b.departure, b.reason = _bus_status_context(b)

    total_routes = len({(b.route or '').strip() for b in buses if (b.route or '').strip()})

    return render(request, 'passenger_dashboard.html', {
        'buses': buses,
        'on_road': on_road,
        'free_seats': free_seats,
        'total_routes': total_routes,
        'total_buses': len(buses),
    })


@admin_required
def admin_dashboard(request):
    """Admin point of view.

    Signed-in staff get the full, scoped fleet-management dashboard.
    """
    from django.db.models import Avg, Count, Sum
    from django.utils import timezone as dj_timezone
    from apps.scoping import (
        scoped_buses, scoped_drivers, scoped_incidents,
        scoped_maintenances, scoped_trips,
    )
    from apps.bus.models import Bus
    from apps.incidents.models import Incident
    from apps.maintenance.models import MaintenanceRecord
    from apps.trips.models import Trip

    buses_qs = scoped_buses(request.user)
    drivers_qs = scoped_drivers(request.user)
    incidents_qs = scoped_incidents(request.user)
    maintenances_qs = scoped_maintenances(request.user)
    trips_qs = scoped_trips(request.user)

    buses_qs = buses_qs.annotate(
        total_passengers=Count('passengers', distinct=True)
    )

    total_buses = buses_qs.count()
    active_buses = buses_qs.filter(status=Bus.STATUS_ACTIVE).count()
    maintenance_buses = buses_qs.filter(status=Bus.STATUS_MAINTENANCE).count()
    total_drivers = drivers_qs.count()
    total_routes = buses_qs.values('route').distinct().count()
    gps_tracked = buses_qs.filter(latitude__isnull=False, longitude__isnull=False).count()

    capacity_sum = buses_qs.aggregate(total=Sum('capacity'))['total'] or 0
    occupied_sum = 0
    available_seats = 0
    available_buses = 0
    for b in buses_qs:
        occupied = b.total_passengers or 0
        occupied_sum += occupied
        left = max(0, (b.capacity or 0) - occupied)
        available_seats += left
        if b.status == Bus.STATUS_ACTIVE and left > 0:
            available_buses += 1

    recent_buses = list(
        buses_qs.prefetch_related('drivers').order_by('-updated_at')[:8]
    )
    for b in recent_buses:
        occupied = b.total_passengers or 0
        b.seats_left = max(0, (b.capacity or 0) - occupied)
        b.occupancy_pct = int(round(occupied * 100.0 / b.capacity)) if b.capacity else 0
        first_driver = None
        try:
            first_driver = b.drivers.all()[0] if hasattr(b, 'drivers') else None
        except Exception:
            first_driver = None
        b.driver_name = first_driver.name if first_driver else '—'
        b.display_location = b.current_location or b.route

    today = dj_timezone.localdate()
    total_trips = trips_qs.count()
    delayed_trips = trips_qs.filter(status=Trip.STATUS_DELAYED).count()
    alert_trips = list(
        trips_qs.select_related('bus').filter(
            status__in=[Trip.STATUS_DELAYED, Trip.STATUS_REROUTED, Trip.STATUS_UNEXPECTED_STOP]
        ).order_by('-updated_at')[:5]
    )
    avg_delay = trips_qs.aggregate(v=Avg('delay_minutes'))['v'] or 0
    total_riders = trips_qs.aggregate(v=Sum('passenger_count'))['v'] or 0
    completed_trips = trips_qs.filter(status__in=[Trip.STATUS_COMPLETED, Trip.STATUS_ON_TIME]).count()
    on_time_pct = round(completed_trips * 100.0 / total_trips, 1) if total_trips else 0

    open_incidents = list(
        incidents_qs.select_related('bus').filter(
            status__in=[Incident.STATUS_REPORTED, Incident.STATUS_RESPONDING]
        ).order_by('-created_at')[:5]
    )
    open_incident_count = incidents_qs.filter(
        status__in=[Incident.STATUS_REPORTED, Incident.STATUS_RESPONDING]
    ).count()

    overdue_maintenance = list(
        maintenances_qs.select_related('bus').filter(
            status__in=[MaintenanceRecord.STATUS_SCHEDULED, MaintenanceRecord.STATUS_OVERDUE],
            next_due_date__lt=today,
        ).order_by('next_due_date')[:5]
    )
    pending_maintenance = maintenances_qs.exclude(
        status=MaintenanceRecord.STATUS_COMPLETED
    ).count()

    alert_count = len(alert_trips) + open_incident_count + len(overdue_maintenance)

    context = {
        'is_admin': True,
        'today': today,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'maintenance_buses': maintenance_buses,
        'available_buses': available_buses,
        'total_drivers': total_drivers,
        'total_routes': total_routes,
        'gps_tracked': gps_tracked,
        'capacity_sum': capacity_sum,
        'occupied_sum': occupied_sum,
        'available_seats': available_seats,
        'recent_buses': recent_buses,
        'total_trips': total_trips,
        'delayed_trips': delayed_trips,
        'alert_trips': alert_trips,
        'avg_delay': round(avg_delay, 1),
        'total_riders': total_riders,
        'on_time_pct': on_time_pct,
        'open_incidents': open_incidents,
        'open_incident_count': open_incident_count,
        'overdue_maintenance': overdue_maintenance,
        'pending_maintenance': pending_maintenance,
        'alert_count': alert_count,
    }
    return render(request, 'home.html', context)


@conductor_required
def conductor_dashboard(request):
    """Conductor point of view: terminal QR scanner and terminal monitor only."""
    from apps.bus import terminal_directory
    from apps.bus.models import Bus
    from apps.bus.views import _staff_terminal, _staff_terminal_id_for_user

    terminal = _staff_terminal(_staff_terminal_id_for_user(request.user))
    if terminal:
        entry = terminal_directory.match_terminal(terminal.get('name'))
        if entry is not None:
            terminal['slug'] = entry['slug']
    recent_scans = (
        Bus.objects.filter(status=Bus.STATUS_ACTIVE)
        .order_by('-updated_at')[:6]
    )
    return render(request, 'conductor_dashboard.html', {
        'terminal': terminal,
        'recent_buses': recent_scans,
    })


@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect(landing_url_name(get_role(request.user)))

    if request.method == 'GET':
        return render(request, 'auth/register.html')

    form_data = {
        'username': request.POST.get('username', ''),
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', ''),
        'email': request.POST.get('email', ''),
        'password': request.POST.get('password', ''),
        'confirm_password': request.POST.get('confirm_password', ''),
    }

    errors = _validate_registration_data(form_data)
    if errors:
        return render(request, 'auth/register.html', {'errors': errors, 'form_data': form_data})

    user = User.objects.create_user(
        username=form_data['username'].strip(),
        first_name=form_data['first_name'].strip(),
        last_name=form_data['last_name'].strip(),
        email=form_data['email'].strip(),
        password=form_data['password'],
    )
    login(request, user)
    messages.success(request, 'Account created. Welcome aboard!')
    return redirect('dashboard')
