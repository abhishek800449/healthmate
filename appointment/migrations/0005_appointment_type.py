# Generated by Django 3.2.5 on 2024-03-23 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0004_auto_20240221_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='type',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
