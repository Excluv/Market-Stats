# Generated by Django 5.0.1 on 2024-03-23 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0006_rename_value_actual_newsreleasedata_value_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsheadline',
            name='measurement',
            field=models.CharField(max_length=100),
        ),
    ]
