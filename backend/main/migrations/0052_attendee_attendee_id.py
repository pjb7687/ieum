from django.db import migrations, models


def copy_id_to_attendee_nametag_id(apps, schema_editor):
    Attendee = apps.get_model('main', 'Attendee')
    for attendee in Attendee.objects.all():
        attendee.attendee_nametag_id = attendee.id
        attendee.save(update_fields=['attendee_nametag_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_speaker_korean_name_affiliation_ko'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='attendee_nametag_id',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(copy_id_to_attendee_nametag_id, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='attendee',
            unique_together={('event', 'attendee_nametag_id')},
        ),
    ]
