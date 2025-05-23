# Generated by Django 5.1.7 on 2025-03-30 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled'), ('completed', 'Completed')], max_length=20)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('pickup_date', models.DateField(blank=True, null=True)),
                ('payment_method', models.CharField(blank=True, choices=[('momo', 'Momo'), ('other', 'Other')], max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
