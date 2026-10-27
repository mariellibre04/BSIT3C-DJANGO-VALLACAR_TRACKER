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
