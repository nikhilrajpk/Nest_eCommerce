# Generated by Django 5.1.1 on 2024-11-14 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0005_product_height_product_length_product_width'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='offer',
        ),
        migrations.DeleteModel(
            name='Offer',
        ),
    ]
