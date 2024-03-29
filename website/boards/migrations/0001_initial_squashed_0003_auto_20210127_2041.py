# Generated by Django 3.0.9 on 2021-01-27 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('boards', '0001_initial'), ('boards', '0002_auto_20210127_2034'), ('boards', '0003_auto_20210127_2041')]

    dependencies = [
        ('members', '0003_auto_20201221_1620'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField()),
                ('end', models.DateField(blank=True, null=True)),
                ('picture', models.ImageField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='BoardMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('function', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('picture', models.ImageField(upload_to='')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.Board')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.Member')),
            ],
        ),
        migrations.AddField(
            model_name='board',
            name='members',
            field=models.ManyToManyField(through='boards.BoardMembership', to='members.Member'),
        ),
    ]
