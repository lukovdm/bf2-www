# Generated by Django 3.2 on 2021-08-22 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0027_auto_20210811_1527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='picture_publication_acceptation',
        ),
    ]