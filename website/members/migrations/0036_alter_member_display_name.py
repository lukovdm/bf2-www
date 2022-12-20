# Generated by Django 4.0 on 2022-12-20 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0035_alter_member_display_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='display_name',
            field=models.CharField(choices=[('Firstname', 'First name'), ('Fullname', 'Full name'), ('Initials', 'Initial with last name'), ('Nickname', 'Nickname'), ('FullnameNickname', 'Full name with nickname'), ('FirstnameNickname', 'First name with nickname')], default='Firstname', max_length=64, verbose_name='display name'),
        ),
    ]