# Generated by Django 5.1.1 on 2024-11-27 04:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_wallet'),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('CREDIT', 'Credit'), ('DEBIT', 'Debit')], max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='home.wallet')),
            ],
        ),
    ]
