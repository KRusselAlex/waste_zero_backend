# Generated by Django 5.1.7 on 2025-03-30 13:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('consumers', '0001_initial'),
        ('offers', '0002_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='consumer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consumers.consumer'),
        ),
        migrations.AddField(
            model_name='order',
            name='offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offers.offer'),
        ),
    ]
