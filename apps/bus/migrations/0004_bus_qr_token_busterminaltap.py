import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def fill_qr_tokens(apps, schema_editor):
    Bus = apps.get_model('bus', 'Bus')
    for bus in Bus.objects.filter(qr_token__isnull=True):
        bus.qr_token = uuid.uuid4()
        bus.save(update_fields=['qr_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('bus', '0003_bus_movement_reason'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='qr_token',
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.RunPython(fill_qr_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='bus',
            name='qr_token',
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, unique=True,
                help_text='Unique token embedded in this bus QR code.',
            ),
        ),
        migrations.CreateModel(
            name='BusTerminalTap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('terminal_name', models.CharField(max_length=255)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('tapped_at', models.DateTimeField(auto_now_add=True)),
                ('bus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminal_taps', to='bus.bus')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='terminal_taps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tblbusterminaltap',
                'ordering': ['-tapped_at'],
            },
        ),
    ]
