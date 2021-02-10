# Generated by Django 3.0.9 on 2021-01-30 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_auto_20201221_1620'),
        ('boards', '0001_initial_squashed_0003_auto_20210127_2041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='members',
        ),
        migrations.AddField(
            model_name='boardmembership',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='board',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='boardmembership',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.Member'),
        ),
        migrations.AlterField(
            model_name='boardmembership',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]