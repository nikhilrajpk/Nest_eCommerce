# Generated by Django 5.1.1 on 2024-11-10 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0011_alter_order_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(blank=True, default='pending', max_length=50, null=True),
        ),
    ]
