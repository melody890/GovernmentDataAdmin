# Generated by Django 3.0.2 on 2020-03-05 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0006_auto_20200305_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='achive',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='event', to='event.Achieve'),
        ),
    ]
