# Generated by Django 5.0.1 on 2024-02-27 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_newsheadline_definition'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='newsreleasedata',
            options={'verbose_name_plural': 'News release data'},
        ),
        migrations.RenameField(
            model_name='newsreleasedata',
            old_name='release_date',
            new_name='date',
        ),
    ]
