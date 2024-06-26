# Generated by Django 5.0.3 on 2024-03-31 21:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20240324_2020'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('signature', models.ImageField(upload_to='signatures/')),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.doctorprofile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.patientprofile')),
            ],
        ),
        migrations.CreateModel(
            name='PrescriptionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
                ('days', models.IntegerField()),
                ('morning', models.BooleanField(default=False)),
                ('afternoon', models.BooleanField(default=False)),
                ('evening', models.BooleanField(default=False)),
                ('night', models.BooleanField(default=False)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.prescription')),
            ],
        ),
    ]
