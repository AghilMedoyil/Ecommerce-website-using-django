# Generated by Django 5.1.1 on 2024-10-17 11:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0003_alter_product_delete_status_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multiimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='admin_side.product'),
        ),
    ]
