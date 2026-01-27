# Generated migration for splitting venue into venue_name and venue_address

from django.db import migrations, models


def migrate_venue_data(apps, schema_editor):
    """Copy existing venue data to venue_name field"""
    Event = apps.get_model('main', 'Event')
    for event in Event.objects.all():
        event.venue_name = event.venue
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_institution'),
    ]

    operations = [
        # Add new fields
        migrations.AddField(
            model_name='event',
            name='venue_name',
            field=models.CharField(max_length=1000, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='event',
            name='venue_address',
            field=models.CharField(max_length=1000, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='event',
            name='venue_latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='venue_longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        # Migrate existing data
        migrations.RunPython(migrate_venue_data, migrations.RunPython.noop),
        # Remove old venue field
        migrations.RemoveField(
            model_name='event',
            name='venue',
        ),
        # Rename venue_name to venue for backwards compatibility
        migrations.RenameField(
            model_name='event',
            old_name='venue_name',
            new_name='venue',
        ),
        # Make venue field not blank
        migrations.AlterField(
            model_name='event',
            name='venue',
            field=models.CharField(max_length=1000),
        ),
    ]
