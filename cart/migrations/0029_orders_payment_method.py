# Generated by Django 5.1.1 on 2024-11-19 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0028_orders_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='payment_method',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
