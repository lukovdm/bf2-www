# Generated by Django 4.0 on 2022-12-21 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0037_alter_member_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='pronouns',
            field=models.CharField(blank=True, help_text='Please write this in english', max_length=256, null=True, verbose_name='pronouns'),
        ),
    ]
