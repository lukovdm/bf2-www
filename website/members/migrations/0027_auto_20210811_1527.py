# Generated by Django 3.1.7 on 2021-08-11 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0026_merge_20210811_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='gender',
            field=models.CharField(choices=[('Man', 'man'), ('Woman', 'woman'), ('Other', 'other'), ('Unspecified', 'unspecified')], max_length=64, verbose_name='gender'),
        ),
    ]
