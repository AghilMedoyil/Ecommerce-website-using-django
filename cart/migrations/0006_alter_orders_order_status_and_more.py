# Generated by Django 5.1.1 on 2024-11-01 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_alter_orders_user_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Refund', 'Refund'), ('Dispatch', 'Dispatch'), ('Return', 'Return')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='orders',
            name='product_quantity',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
