# Generated by Django 5.1.1 on 2024-11-04 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0008_rename_transaction_id_payment_razor_pay_order_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]