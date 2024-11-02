# Generated by Django 5.1.1 on 2024-11-02 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0007_orderitems_return_date_orderitems_return_reason_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='transaction_id',
            new_name='razor_pay_order_id',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='payment_status',
        ),
        migrations.AddField(
            model_name='payment',
            name='razor_pay_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='razor_pay_payment_signature',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]