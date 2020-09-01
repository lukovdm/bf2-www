# Generated by Django 3.0.9 on 2020-09-01 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='participant limit',
        ),
        migrations.AddField(
            model_name='event',
            name='limit',
            field=models.IntegerField(null=True, verbose_name='participant limit'),
        ),
    ]
