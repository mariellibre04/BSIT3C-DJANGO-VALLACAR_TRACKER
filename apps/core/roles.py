"""Role helpers shared by the admin, conductor and passenger experiences."""

from django.contrib.auth.models import Group

ROLE_ADMIN = 'admin'
ROLE_CONDUCTOR = 'conductor'
ROLE_PASSENGER = 'passenger'

ROLE_CHOICES = (
    (ROLE_ADMIN, 'Administrator'),
    (ROLE_CONDUCTOR, 'Conductor'),
    (ROLE_PASSENGER, 'Passenger'),
)

ROLE_LABELS = dict(ROLE_CHOICES)

GROUP_NAMES = {
    ROLE_ADMIN: 'Administrator',
    ROLE_CONDUCTOR: 'Conductor',
    ROLE_PASSENGER: 'Passenger',
}


def ensure_role_groups():
    """Create the role groups if they do not exist yet."""
    groups = {}
    for role, name in GROUP_NAMES.items():
        groups[role], _created = Group.objects.get_or_create(name=name)
    return groups


def get_role(user):
    """Return the effective role for a user (passenger for anonymous users)."""
    if not user or not getattr(user, 'is_authenticated', False):
        return ROLE_PASSENGER
    if user.is_superuser:
        return ROLE_ADMIN
    if user.groups.filter(name=GROUP_NAMES[ROLE_CONDUCTOR]).exists():
        return ROLE_CONDUCTOR
    if user.is_staff:
        return ROLE_ADMIN
    return ROLE_PASSENGER


def role_label(user):
    return ROLE_LABELS.get(get_role(user), 'Passenger')


def set_role(user, role):
    """Assign a role to a user, keeping Django staff/superuser flags in sync."""
    if role not in ROLE_LABELS:
        role = ROLE_PASSENGER
    if user.is_superuser:
        role = ROLE_ADMIN

    groups = ensure_role_groups()
    user.groups.remove(*groups.values())
    user.groups.add(groups[role])

    if not user.is_superuser:
        user.is_staff = role == ROLE_ADMIN
        user.save(update_fields=['is_staff'])
    return role


def landing_url_name(role):
    if role == ROLE_ADMIN:
        return 'admin_dashboard'
    if role == ROLE_CONDUCTOR:
        return 'conductor_dashboard'
    return 'dashboard'
