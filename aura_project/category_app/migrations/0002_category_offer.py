# Generated by Django 5.1.1 on 2024-11-14 16:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category_app', '0001_initial'),
        ('offer_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='offer_app.offer'),
        ),
    ]