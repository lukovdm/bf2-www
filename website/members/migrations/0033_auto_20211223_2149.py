# Generated by Django 3.2 on 2021-12-23 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0032_merge_20210822_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='bio',
            field=models.TextField(blank=True, null=True, verbose_name='bio'),
        ),
        migrations.AddField(
            model_name='member',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
