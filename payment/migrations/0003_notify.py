# Generated by Django 5.0 on 2024-04-01 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_rename_date_payments_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='notify',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
