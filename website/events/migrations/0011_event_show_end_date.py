# Generated by Django 3.2 on 2021-11-02 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_event_private_registrations'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='show_end_date',
            field=models.BooleanField(default=True, verbose_name='Show end date'),
        ),
    ]
