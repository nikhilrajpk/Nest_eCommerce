# Generated by Django 5.1.1 on 2024-11-01 02:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransation',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='wallet_app.wallet'),
        ),
    ]
