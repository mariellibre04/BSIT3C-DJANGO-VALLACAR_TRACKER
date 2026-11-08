"""Restrict the route/terminal catalogue to Negros Occidental.

The tracker previously seeded nationwide terminals and Negros Oriental /
Cebu routes. This one-time data migration removes every route that is not in
the Negros Occidental catalogue, drops terminals outside the province, and
then re-seeds the curated Negros Occidental master list.
"""

from django.db import migrations
from django.db.models import Q


def scope_negros_occidental(apps, schema_editor):
    from apps.bus.route_config import ROUTE_DEFINITIONS, TERMINAL_MASTER_LIST
    from apps.bus.route_service import seed_transit_data

    Route = apps.get_model('bus', 'Route')
    Terminal = apps.get_model('bus', 'Terminal')
    BusNextStopLog = apps.get_model('bus', 'BusNextStopLog')

    allowed_terminals = {
        entry['name'] for entry in TERMINAL_MASTER_LIST
    }

    # BusNextStopLog protects its terminal FKs, so drop logs that point at
    # stops outside Negros Occidental before the terminals are pruned.
    out_of_scope = Terminal.objects.exclude(name__in=allowed_terminals)
    BusNextStopLog.objects.filter(
        Q(current_station__in=out_of_scope) | Q(next_stop__in=out_of_scope)
    ).delete()

    # Route origin/destination and RouteStop.terminal are PROTECT foreign
    # keys. Clear every route (cascading its stops) and rebuild the catalogue
    # from the curated Negros Occidental definitions below.
    Route.objects.all().delete()
    out_of_scope.delete()

    seed_transit_data(force=True)


class Migration(migrations.Migration):

    dependencies = [
        ('bus', '0010_alter_bus_next_stop'),
    ]

    operations = [
        migrations.RunPython(
            scope_negros_occidental,
            migrations.RunPython.noop,
        ),
    ]
