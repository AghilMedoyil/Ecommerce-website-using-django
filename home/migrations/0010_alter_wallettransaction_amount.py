# Generated by Django 5.1.1 on 2024-12-06 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_alter_wallettransaction_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
