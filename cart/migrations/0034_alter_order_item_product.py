# Generated by Django 5.1.1 on 2024-11-23 06:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0016_productoffer_description_productoffer_name'),
        ('cart', '0033_alter_order_item_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_item',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orderitems', to='admin_side.product'),
        ),
    ]
