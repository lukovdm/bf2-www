# Generated by Django 3.1.7 on 2021-07-01 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0022_merge_20210624_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='gender',
            field=models.CharField(choices=[('Male', 'male'), ('Female', 'female'), ('Other', 'other'), ('Unspecified', 'unspecified')], max_length=64, verbose_name='gender'),
        ),
    ]