"""Bus records for Vallacar Tracker."""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Bus(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_MAINTENANCE = 'maintenance'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_MAINTENANCE, 'Maintenance'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    MOVE_AT_TERMINAL = 'at_terminal'
    MOVE_EN_ROUTE = 'en_route'
    MOVE_STOPPED = 'stopped'
    MOVE_DELAYED = 'delayed'
    MOVE_OFF_ROUTE = 'off_route'
    MOVEMENT_CHOICES = [
        (MOVE_AT_TERMINAL, 'At Terminal'),
        (MOVE_EN_ROUTE, 'En Route'),
        (MOVE_STOPPED, 'Stopped'),
        (MOVE_DELAYED, 'Delayed'),
        (MOVE_OFF_ROUTE, 'Off Route'),
    ]

    bus_number = models.CharField(max_length=50, unique=True)
    plate_number = models.CharField(max_length=20, unique=True)
    qr_token = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False,
        help_text='Unique token embedded in this bus QR code.',
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    route = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    # 1. Real-Time GPS Tracking: current location + coordinates + movement
    current_location = models.CharField(
        max_length=255, blank=True, default='',
        help_text='Latest known location, e.g. Bacolod North Terminal - Bay 3',
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text='GPS latitude, e.g. 10.676500',
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text='GPS longitude, e.g. 122.950900',
    )
    movement_status = models.CharField(
        max_length=20, choices=MOVEMENT_CHOICES, default=MOVE_AT_TERMINAL
    )
    movement_reason = models.CharField(
        max_length=255, blank=True, default='',
        help_text='Why the bus is delayed or stopped, shown to passengers.',
    )
    last_gps_update = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='buses',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblbus'
        ordering = ['bus_number']

    def __str__(self):
        return f'{self.bus_number} ({self.plate_number})'

    @property
    def assigned_count(self):
        return self.passengers.count()

    @property
    def available_seats(self):
        return max(0, self.capacity - self.assigned_count)

    @property
    def is_full(self):
        return self.available_seats <= 0


class Terminal(models.Model):
    """A Vallacar terminal or a major stop on a Vallacar route.

    Names are kept unique so route sequences and conductor scans can be
    matched back to the master list without guessing.
    """

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(
        max_length=30, unique=True, blank=True,
        help_text='Short terminal/stop code, e.g. KAB or DGT.',
    )
    city = models.CharField(max_length=255, blank=True)
    province = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_owned_terminal = models.BooleanField(
        default=False,
        help_text='True when Vallacar owns/operates the terminal itself.',
    )
    is_major_stop = models.BooleanField(
        default=True,
        help_text='True when the place is a major stop on a Vallacar route.',
    )
    source = models.CharField(
        max_length=255, blank=True,
        help_text='Where this terminal/stop entry was verified from.',
    )
    aliases = models.CharField(
        max_length=255, blank=True,
        help_text='Comma-separated alternate names used in bus.route text.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblterminal'
        ordering = ['name']

    def __str__(self):
        return self.name


class Route(models.Model):
    """A validated (or source-compiled) ordered bus route."""

    STATUS_SOURCE_COMPILED = 'source_compiled'
    STATUS_CONDUCTOR_VALIDATED = 'conductor_validated'
    STATUS_PENDING = 'pending'
    VALIDATION_CHOICES = [
        (STATUS_SOURCE_COMPILED, 'Source compiled'),
        (STATUS_CONDUCTOR_VALIDATED, 'Conductor validated'),
        (STATUS_PENDING, 'Pending validation'),
    ]

    name = models.CharField(max_length=255, unique=True)
    origin = models.ForeignKey(
        Terminal,
        related_name='routes_origin',
        on_delete=models.PROTECT,
    )
    destination = models.ForeignKey(
        Terminal,
        related_name='routes_destination',
        on_delete=models.PROTECT,
    )
    validation_status = models.CharField(
        max_length=30, choices=VALIDATION_CHOICES, default=STATUS_PENDING
    )
    validation_note = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    aliases = models.CharField(
        max_length=255, blank=True,
        help_text='Comma-separated alternate route names.',
    )
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='validated_routes',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblroute'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_usable(self):
        return self.validation_status in (
            self.STATUS_SOURCE_COMPILED,
            self.STATUS_CONDUCTOR_VALIDATED,
        )


class RouteStop(models.Model):
    """One ordered stop on a route."""

    route = models.ForeignKey(Route, related_name='stops', on_delete=models.CASCADE)
    terminal = models.ForeignKey(
        Terminal, related_name='route_stops', on_delete=models.PROTECT
    )
    sequence = models.PositiveIntegerField(
        help_text='1-based order of the stop within the route.'
    )
    distance_from_previous_km = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        help_text='Road distance from the previous stop in kilometres.',
    )
    average_speed_kmh = models.PositiveIntegerField(
        default=45,
        help_text='Average speed for the segment ending at this stop.',
    )

    class Meta:
        db_table = 'tblroutestop'
        ordering = ['route', 'sequence']
        constraints = [
            models.UniqueConstraint(
                fields=['route', 'terminal'], name='uniq_route_terminal'
            ),
            models.UniqueConstraint(
                fields=['route', 'sequence'], name='uniq_route_sequence'
            ),
        ]

    def __str__(self):
        return f'{self.route.name} #{self.sequence} {self.terminal.name}'


class BusNextStopLog(models.Model):
    """Conductor-selected next stop with its computed ETA."""

    bus = models.ForeignKey(
        Bus, related_name='next_stop_logs', on_delete=models.CASCADE
    )
    route = models.ForeignKey(
        Route, related_name='next_stop_logs', on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    current_station = models.ForeignKey(
        Terminal, related_name='next_stop_from_logs', on_delete=models.PROTECT
    )
    next_stop = models.ForeignKey(
        Terminal, related_name='next_stop_to_logs', on_delete=models.PROTECT
    )
    distance_km = models.DecimalField(max_digits=7, decimal_places=2)
    average_speed_kmh = models.PositiveIntegerField()
    eta_minutes = models.PositiveIntegerField()
    eta_at = models.DateTimeField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='bus_next_stop_logs',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tblbusnextstoplog'
        ordering = ['-logged_at']

    def __str__(self):
        return (
            f'{self.bus.bus_number}: {self.current_station.name} -> '
            f'{self.next_stop.name}'
        )


class BusTerminalTap(models.Model):
    """A conductor scan of a bus QR code at a terminal."""

    bus = models.ForeignKey(
        Bus,
        related_name='terminal_taps',
        on_delete=models.CASCADE,
    )
    terminal_name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='terminal_taps',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tapped_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tblbusterminaltap'
        ordering = ['-tapped_at']

    def __str__(self):
        return f'{self.bus.bus_number} @ {self.terminal_name}'
