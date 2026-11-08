from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bus', '0011_scope_negros_occidental'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusStop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('sequence', models.PositiveIntegerField(help_text='1-based order of the stop for this bus.')),
                ('eta', models.TimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_stops', to='bus.bus')),
            ],
            options={
                'db_table': 'tblbusstop',
                'ordering': ['bus', 'sequence'],
                'constraints': [models.UniqueConstraint(fields=('bus', 'sequence'), name='uniq_bus_stop_sequence')],
            },
        ),
    ]
