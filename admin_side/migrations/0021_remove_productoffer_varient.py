# Generated by Django 5.1.1 on 2024-12-04 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0020_productoffer_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productoffer',
            name='Varient',
        ),
    ]