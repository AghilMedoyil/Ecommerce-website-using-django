# Generated by Django 5.1.1 on 2024-11-04 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0012_orders_grand_total_orders_shipping_price_orders_tax'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='cancellation_reason',
            field=models.TextField(default=None),
        ),
    ]
