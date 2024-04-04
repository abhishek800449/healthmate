# Generated by Django 5.0.3 on 2024-04-04 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0015_prescription_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('billing_address', models.CharField(max_length=100)),
                ('payment_method', models.CharField(max_length=20)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=100)),
                ('issue_date', models.DateField(auto_now_add=True)),
                ('doctor_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.doctorprofile')),
                ('patient_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.patientprofile')),
            ],
        ),
    ]
