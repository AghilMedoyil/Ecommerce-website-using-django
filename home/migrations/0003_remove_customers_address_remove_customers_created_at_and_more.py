# Generated by Django 5.1.1 on 2024-10-22 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_remove_products_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customers',
            name='address',
        ),
        migrations.RemoveField(
            model_name='customers',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='customers',
            name='delete_status',
        ),
        migrations.RemoveField(
            model_name='customers',
            name='name',
        ),
        migrations.RemoveField(
            model_name='customers',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='customers',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='customers',
            name='user',
        ),
    ]
