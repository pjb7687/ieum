from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_user_deletion_warning_sent'),
    ]

    operations = [
        # Create AccountSettings singleton model
        migrations.CreateModel(
            name='AccountSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_deletion_period', models.IntegerField(default=1095)),  # 3 years in days
                ('account_warning_period', models.IntegerField(default=7)),
                ('attendee_retention_years', models.IntegerField(default=5)),
                ('payment_retention_years', models.IntegerField(default=5)),
            ],
            options={
                'verbose_name': 'Account Settings',
                'verbose_name_plural': 'Account Settings',
            },
        ),
        # Add user_deleted_at field to Attendee
        migrations.AddField(
            model_name='attendee',
            name='user_deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add user_email field to Attendee
        migrations.AddField(
            model_name='attendee',
            name='user_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        # Change Attendee.user to allow null (SET_NULL on delete)
        migrations.AlterField(
            model_name='attendee',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
