# Generated by Django 5.0.3 on 2024-04-06 18:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0015_prescription_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255, null=True)),
                ('image', models.ImageField(blank=True, upload_to='lab_test_images')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='LabTestBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=50)),
                ('booking_date', models.DateField(auto_now_add=True)),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField()),
                ('phone_number', models.CharField(max_length=12)),
                ('remarks', models.CharField(max_length=255, null=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('zip_code', models.CharField(max_length=20)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.city')),
                ('lab_test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='labs.labtest')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.patientprofile')),
            ],
        ),
    ]
