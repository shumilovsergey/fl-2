# Generated by Django 4.2.3 on 2023-07-27 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_moderators_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='janras',
            old_name='janra',
            new_name='name',
        ),
    ]
