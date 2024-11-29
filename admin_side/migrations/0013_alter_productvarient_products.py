# Generated by Django 5.1.1 on 2024-11-05 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0012_rename_adjusted_price_productvarient_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvarient',
            name='products',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='varients', to='admin_side.product'),
        ),
    ]
