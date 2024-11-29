# Generated by Django 5.1.1 on 2024-11-04 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0011_alter_orders_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='grand_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orders',
            name='shipping_price',
            field=models.DecimalField(decimal_places=2, default=30.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orders',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=10.0, max_digits=10),
        ),
    ]