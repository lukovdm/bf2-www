# Generated by Django 3.0.9 on 2021-02-24 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_auto_20210224_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='student_type',
            field=models.CharField(blank=True, choices=[('RU', 'Radboud University'), ('HAN', 'HAN'), ('NS', 'Not a student')], max_length=3, null=True, verbose_name='student type'),
        ),
    ]
