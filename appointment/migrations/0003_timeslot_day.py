# Generated by Django 3.2.5 on 2023-11-21 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0002_auto_20231116_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='day',
            field=models.CharField(blank=True, choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=10, null=True),
        ),
    ]
