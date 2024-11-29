# Generated by Django 5.1.1 on 2024-10-16 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0002_alter_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='delete_status',
            field=models.IntegerField(blank=True, choices=[(1, 'live'), (0, 'delete')], default=1, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='products/'),
        ),
    ]
