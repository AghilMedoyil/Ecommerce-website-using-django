# Generated by Django 5.1.1 on 2024-11-21 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='head',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
