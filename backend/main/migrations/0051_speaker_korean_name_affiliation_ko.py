from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_add_organizers_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='speaker',
            name='korean_name',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='speaker',
            name='affiliation_ko',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
