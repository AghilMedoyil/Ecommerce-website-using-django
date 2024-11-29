# Generated by Django 5.1.1 on 2024-11-08 09:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0013_alter_productvarient_products'),
        ('cart', '0021_remove_cart_grand_total_wishlist_wishlistitem_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlistitem',
            name='varient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='admin_side.productvarient'),
            preserve_default=False,
        ),
    ]
