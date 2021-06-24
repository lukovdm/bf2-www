# Generated by Django 3.2 on 2021-06-24 11:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0018_merge_20210420_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='gender',
            field=models.CharField(default='Female', max_length=64, verbose_name='gender'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='google_email',
            field=models.EmailField(default='', max_length=254, verbose_name='google email'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='picture_publication_acceptation',
            field=models.BooleanField(choices=[('Yes', 'Yes'), ('No', 'No')], default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='member',
            name='graduation_date',
            field=models.DateField(blank=True, null=True, verbose_name='graduation date'),
        ),
        migrations.AlterField(
            model_name='member',
            name='sports_card_number',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(code='invalid_sports_card_number', message='sports card number must be in the form ......', regex='^([su]\\d)?\\d{6}$')], verbose_name='sports card number'),
        ),
    ]
