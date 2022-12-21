# Generated by Django 3.2 on 2021-12-17 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('committees', '0003_auto_20211217_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committee',
            name='perm_group',
            field=models.OneToOneField(blank=True, help_text="You can set permission here, but don't change it", null=True, on_delete=django.db.models.deletion.PROTECT, to='auth.group', verbose_name='Permissions'),
        ),
    ]
