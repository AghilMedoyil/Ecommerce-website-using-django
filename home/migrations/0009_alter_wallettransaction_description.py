# Generated by Django 5.1.1 on 2024-12-06 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_alter_wallettransaction_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='description',
            field=models.TextField(),
        ),
    ]