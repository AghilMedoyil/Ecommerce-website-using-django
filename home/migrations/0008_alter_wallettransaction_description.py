# Generated by Django 5.1.1 on 2024-12-06 12:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_wallettransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='description',
            field=models.TextField(default=django.utils.timezone.now),
        ),
    ]