from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_privacypolicy'),
    ]

    operations = [
        migrations.CreateModel(
            name='TermsOfService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_en', models.TextField(blank=True, default='')),
                ('content_ko', models.TextField(blank=True, default='')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Terms of Service',
                'verbose_name_plural': 'Terms of Service',
            },
        ),
    ]
