# Generated by Django 5.0.3 on 2024-04-14 12:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_prescription_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalrecord',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
