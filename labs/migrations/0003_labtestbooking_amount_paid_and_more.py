# Generated by Django 5.0.3 on 2024-04-12 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labs', '0002_pendinglabbooking'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtestbooking',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='pendinglabbooking',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
