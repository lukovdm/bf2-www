# Generated by Django 3.2 on 2022-11-23 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_alter_event_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='cost',
        ),
        migrations.AddField(
            model_name='event',
            name='cost_en',
            field=models.CharField(max_length=255, null=True, verbose_name='cost (NL) (EN)'),
        ),
        migrations.AddField(
            model_name='event',
            name='cost_nl',
            field=models.CharField(max_length=255, null=True, verbose_name='cost (NL) (NL)'),
        ),
        migrations.AlterField(
            model_name='event',
            name='name_en',
            field=models.CharField(max_length=255, null=True, verbose_name='cost (EN)'),
        ),
        migrations.AlterField(
            model_name='event',
            name='name_nl',
            field=models.CharField(max_length=255, null=True, verbose_name='cost (NL)'),
        ),
    ]
