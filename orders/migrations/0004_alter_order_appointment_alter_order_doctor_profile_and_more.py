# Generated by Django 5.0.3 on 2024-04-10 00:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_prescription_description'),
        ('appointment', '0007_delete_order'),
        ('labs', '0002_pendinglabbooking'),
        ('orders', '0003_order_appointment_order_lab'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='appointment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appointment.appointment'),
        ),
        migrations.AlterField(
            model_name='order',
            name='doctor_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.doctorprofile'),
        ),
        migrations.AlterField(
            model_name='order',
            name='lab',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='labs.labtestbooking'),
        ),
    ]
