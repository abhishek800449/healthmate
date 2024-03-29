# Generated by Django 3.2.5 on 2024-03-24 20:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_doctorprofile_about_me'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctorprofile',
            name='clinic',
        ),
        migrations.AddField(
            model_name='clinic',
            name='doctor',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.doctorprofile'),
        ),
    ]
