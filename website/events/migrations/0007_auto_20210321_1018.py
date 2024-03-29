# Generated by Django 3.1.7 on 2021-03-21 10:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_merge_20210302_2218'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='date',
        ),
        migrations.AddField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='end date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='start date'),
            preserve_default=False,
        ),
    ]
