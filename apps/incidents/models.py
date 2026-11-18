"""Emergency and incident reporting: accidents, breakdowns, resolution tracking."""

from django.conf import settings
from django.db import models


class Incident(models.Model):
    TYPE_ACCIDENT = 'accident'
    TYPE_BREAKDOWN = 'breakdown'
    TYPE_DELAY = 'delay'
    TYPE_PASSENGER_ISSUE = 'passenger_issue'
    TYPE_ROAD_HAZARD = 'road_hazard'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = [
        (TYPE_ACCIDENT, 'Accident'),
        (TYPE_BREAKDOWN, 'Breakdown'),
        (TYPE_DELAY, 'Major Delay'),
        (TYPE_PASSENGER_ISSUE, 'Passenger Issue'),
        (TYPE_ROAD_HAZARD, 'Road Hazard'),
        (TYPE_OTHER, 'Other'),
    ]

    SEVERITY_LOW = 'low'
    SEVERITY_MEDIUM = 'medium'
    SEVERITY_HIGH = 'high'
    SEVERITY_CRITICAL = 'critical'
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, 'Low'),
        (SEVERITY_MEDIUM, 'Medium'),
        (SEVERITY_HIGH, 'High'),
        (SEVERITY_CRITICAL, 'Critical'),
    ]

    STATUS_REPORTED = 'reported'
    STATUS_RESPONDING = 'responding'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_REPORTED, 'Reported'),
        (STATUS_RESPONDING, 'Responding'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]
    OPEN_STATUSES = {STATUS_REPORTED, STATUS_RESPONDING}

    bus = models.ForeignKey(
        'bus.Bus',
        related_name='incidents',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    incident_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_OTHER)
    custom_type = models.CharField(
        max_length=100, blank=True, default='',
        help_text='Free-text type entered when "Other" is selected.',
    )
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_MEDIUM)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REPORTED)
    resolved_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='incidents',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblincident'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_severity_display()} / {self.get_status_display()})'

    @property
    def display_type(self):
        """Friendly type label, including the free-text value for "Other"."""
        if self.incident_type == self.TYPE_OTHER and self.custom_type:
            return self.custom_type
        return self.get_incident_type_display()

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES
