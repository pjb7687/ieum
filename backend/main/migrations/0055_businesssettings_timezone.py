from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_onsiteattendee_nametag_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesssettings',
            name='timezone',
            field=models.CharField(default='Asia/Seoul', max_length=50),
        ),
    ]
