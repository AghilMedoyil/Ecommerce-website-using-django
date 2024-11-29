# Generated by Django 5.1.1 on 2024-10-22 09:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delete_status', models.IntegerField(choices=[(1, 'live'), (0, 'delete')], default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('phone', models.IntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='addresses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delete_status', models.IntegerField(choices=[(1, 'live'), (0, 'delete')], default=1)),
                ('name', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=200)),
                ('landmark', models.CharField(max_length=200)),
                ('district', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200)),
                ('pincode', models.IntegerField()),
                ('Customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userprofile.customer')),
            ],
        ),
    ]