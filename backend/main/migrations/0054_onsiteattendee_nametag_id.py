from django.db import migrations, models


def populate_onsiteattendee_nametag_ids(apps, schema_editor):
    """Assign nametag IDs per event for existing on-site attendees."""
    OnSiteAttendee = apps.get_model('main', 'OnSiteAttendee')
    Event = apps.get_model('main', 'Event')

    for event in Event.objects.all():
        for idx, oa in enumerate(OnSiteAttendee.objects.filter(event=event).order_by('id'), start=1):
            oa.onsiteattendee_nametag_id = idx
            oa.save(update_fields=['onsiteattendee_nametag_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_organizer_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='onsiteattendee',
            name='onsiteattendee_nametag_id',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(populate_onsiteattendee_nametag_ids, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='onsiteattendee',
            unique_together={('event', 'onsiteattendee_nametag_id')},
        ),
    ]
