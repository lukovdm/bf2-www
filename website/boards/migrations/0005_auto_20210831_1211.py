# Generated by Django 3.2 on 2021-08-31 12:11

from django.conf import settings
from django.db import migrations
import django.db.models.deletion
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('boards', '0004_merge_20210302_2121'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='picture',
        ),
        migrations.AddField(
            model_name='board',
            name='picture',
            field=filer.fields.image.FilerImageField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.FILER_IMAGE_MODEL, verbose_name='picture'),
        ),
        migrations.RemoveField(
            model_name='boardmembership',
            name='picture',
        ),
        migrations.AddField(
            model_name='boardmembership',
            name='picture',
            field=filer.fields.image.FilerImageField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.FILER_IMAGE_MODEL, verbose_name='picture'),
        ),
    ]