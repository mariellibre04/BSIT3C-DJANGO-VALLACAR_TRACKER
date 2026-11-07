"""Rename the Cauayan terminal/stop to Narra."""

import re

from django.db import migrations


def _rename(value):
    if not value:
        return value
    value = re.sub(r'\bCauayan Negros\b', 'Narra', value, flags=re.IGNORECASE)
    return re.sub(r'\bCauayan\b', 'Narra', value, flags=re.IGNORECASE)


def rename_cauayan_to_narra(apps, schema_editor):
    Bus = apps.get_model('bus', 'Bus')
    BusTerminalTap = apps.get_model('bus', 'BusTerminalTap')
    Terminal = apps.get_model('bus', 'Terminal')

    bus_fields = [
        'route', 'current_location', 'current_terminal', 'next_stop',
        'next_terminal', 'final_destination',
    ]
    for bus in Bus.objects.all():
        changed = []
        for field in bus_fields:
            old_value = getattr(bus, field)
            new_value = _rename(old_value)
            if new_value != old_value:
                setattr(bus, field, new_value)
                changed.append(field)
        if changed:
            bus.save(update_fields=changed)

    for tap in BusTerminalTap.objects.all():
        new_value = _rename(tap.terminal_name)
        if new_value != tap.terminal_name:
            tap.terminal_name = new_value
            tap.save(update_fields=['terminal_name'])

    for terminal in Terminal.objects.filter(province__iexact='Negros Occidental'):
        changed = []
        if _rename(terminal.name) != terminal.name:
            terminal.name = _rename(terminal.name)
            changed.append('name')
        if _rename(terminal.city) != terminal.city:
            terminal.city = _rename(terminal.city)
            changed.append('city')
        if changed:
            terminal.save(update_fields=changed)


def reverse_rename(apps, schema_editor):
    # The old name is not restored automatically; Narra is the intended name.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('bus', '0008_demoseedstate_bus_next_terminal_and_more'),
    ]

    operations = [
        migrations.RunPython(rename_cauayan_to_narra, reverse_rename),
    ]
