# Generated by Django 5.0.1 on 2024-02-29 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0003_alter_newsreleasedata_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsreleasedata',
            name='value_actual',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='newsreleasedata',
            name='value_forecast',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='newsreleasedata',
            name='value_previous',
            field=models.FloatField(null=True),
        ),
    ]