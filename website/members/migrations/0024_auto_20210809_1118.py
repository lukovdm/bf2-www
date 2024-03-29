# Generated by Django 3.1.7 on 2021-08-09 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0023_alter_member_picture_publication_acceptation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='picture_publication_acceptation',
            field=models.BooleanField(verbose_name='allowed to publish pictures of'),
        ),
        migrations.AlterField(
            model_name='member',
            name='preferred_language',
            field=models.CharField(choices=[('en', 'English'), ('nl', 'Dutch')], default='nl', max_length=3, verbose_name='preferred language'),
        ),
        migrations.AlterField(
            model_name='member',
            name='student_type',
            field=models.CharField(choices=[('RU', 'Radboud University'), ('HAN', 'HAN'), ('NS', 'Not a student')], max_length=3, verbose_name='type of student'),
        ),
    ]
