from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_add_event_is_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='deletion_warning_sent',
            field=models.BooleanField(default=False),
        ),
    ]
