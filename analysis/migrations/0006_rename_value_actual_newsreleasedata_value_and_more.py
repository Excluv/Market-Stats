# Generated by Django 5.0.1 on 2024-03-14 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0005_newsheadline_sector'),
    ]

    operations = [
        migrations.RenameField(
            model_name='newsreleasedata',
            old_name='value_actual',
            new_name='value',
        ),
        migrations.RemoveField(
            model_name='newsreleasedata',
            name='impact',
        ),
        migrations.RemoveField(
            model_name='newsreleasedata',
            name='value_forecast',
        ),
        migrations.RemoveField(
            model_name='newsreleasedata',
            name='value_previous',
        ),
    ]
