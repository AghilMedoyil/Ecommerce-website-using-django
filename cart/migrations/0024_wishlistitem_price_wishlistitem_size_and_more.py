# Generated by Django 5.1.1 on 2024-11-08 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0023_remove_wishlistitem_varient'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlistitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='wishlistitem',
            name='size',
            field=models.PositiveIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='wishlistitem',
            name='variant_stock_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]