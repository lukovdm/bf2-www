# Generated by Django 3.0.9 on 2021-02-24 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_auto_20210224_2042'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='other_club',
            field=models.CharField(blank=True, choices=[('DDT', 'DDT'), ('Ufo', 'Ufo'), ('GD', 'GD'), ('Vertigo', 'Vertigo'), ('AUC', 'AUC')], max_length=10, null=True, verbose_name='other club'),
        ),
    ]
