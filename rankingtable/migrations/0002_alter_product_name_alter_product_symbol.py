# Generated by Django 5.0.1 on 2024-02-19 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rankingtable', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='symbol',
            field=models.CharField(max_length=30),
        ),
    ]
