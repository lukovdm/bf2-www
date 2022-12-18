# Generated by Django 4.0 on 2022-12-14 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_alter_event_form_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='cost',
        ),
        migrations.AddField(
            model_name='event',
            name='cost_en',
            field=models.CharField(max_length=255, null=True, verbose_name='cost (EN)'),
        ),
        migrations.AddField(
            model_name='event',
            name='cost_nl',
            field=models.CharField(max_length=255, null=True, verbose_name='cost (NL)'),
        ),
    ]
