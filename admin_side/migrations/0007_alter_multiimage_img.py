# Generated by Django 5.1.1 on 2024-10-18 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0006_alter_multiimage_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multiimage',
            name='img',
            field=models.ImageField(upload_to='product_images/'),
        ),
    ]
