# Generated by Django 5.1.1 on 2024-10-25 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0002_remove_addresses_address_remove_addresses_landmark_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.IntegerField(null=True),
        ),
    ]
