from django.db import migrations, models
import django.db.models.deletion


def copy_m2m_to_organizer_model(apps, schema_editor):
    """Copy organizer data from M2M relationship to the new Organizer model."""
    Event = apps.get_model('main', 'Event')
    Organizer = apps.get_model('main', 'Organizer')
    User = apps.get_model('main', 'User')

    for event in Event.objects.all():
        organizers = list(event.organizers.all())
        # Sort by saved order if exists
        if event.organizers_order:
            order_map = {uid: idx for idx, uid in enumerate(event.organizers_order)}
            organizers.sort(key=lambda o: order_map.get(o.id, len(order_map)))

        for idx, user in enumerate(organizers):
            name = f"{user.first_name} {user.last_name}".strip()
            korean_name = user.korean_name or ''
            email = user.email or ''
            # Get institution names
            affiliation = ''
            affiliation_ko = ''
            if user.institute:
                affiliation = user.institute.name_en or ''
                affiliation_ko = user.institute.name_ko or ''

            Organizer.objects.create(
                event=event,
                name=name,
                korean_name=korean_name,
                email=email,
                affiliation=affiliation,
                affiliation_ko=affiliation_ko,
                order=idx,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_attendee_attendee_id'),
    ]

    operations = [
        # 1. Create the new Organizer model
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('korean_name', models.CharField(blank=True, default='', max_length=1000)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('affiliation', models.CharField(blank=True, max_length=1000)),
                ('affiliation_ko', models.CharField(blank=True, default='', max_length=1000)),
                ('order', models.PositiveIntegerField(default=0)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organizer_set', to='main.event')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        # 2. Copy data from M2M to new model
        migrations.RunPython(copy_m2m_to_organizer_model, migrations.RunPython.noop),
        # 3. Remove old fields
        migrations.RemoveField(
            model_name='event',
            name='organizers',
        ),
        migrations.RemoveField(
            model_name='event',
            name='organizers_order',
        ),
    ]
