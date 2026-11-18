from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='custom_type',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Free-text type entered when "Other" is selected.',
                max_length=100,
            ),
        ),
    ]
