# Generated by Django 5.1.1 on 2024-11-27 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0017_alter_product_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sold_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
