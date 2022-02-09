# Generated by Django 3.2 on 2022-02-09 14:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_merge_0010_event_form_link_0011_event_show_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='form_link',
            field=models.CharField(blank=True, max_length=128, null=True, validators=[django.core.validators.RegexValidator(message='Please enter a google form share link', regex='https:\\/\\/docs\\.google\\.com\\/forms\\/d\\/e\\/[\\w\\d_-]*\\/viewform\\?')], verbose_name='Google form link'),
        ),
    ]
