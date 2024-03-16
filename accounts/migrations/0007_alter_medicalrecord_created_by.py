# Generated by Django 3.2.5 on 2024-03-16 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_medicalrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalrecord',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.doctorprofile'),
        ),
    ]
