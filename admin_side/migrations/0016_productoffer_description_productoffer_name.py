# Generated by Django 5.1.1 on 2024-11-12 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0015_productoffer_varient'),
    ]

    operations = [
        migrations.AddField(
            model_name='productoffer',
            name='description',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productoffer',
            name='name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
