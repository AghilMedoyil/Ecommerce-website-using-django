# Generated by Django 5.1.1 on 2024-11-21 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0031_alter_orders_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='user_address',
            field=models.TextField(),
        ),
    ]
