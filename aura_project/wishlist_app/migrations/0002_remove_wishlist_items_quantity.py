# Generated by Django 5.1.1 on 2024-10-18 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist_items',
            name='quantity',
        ),
    ]
