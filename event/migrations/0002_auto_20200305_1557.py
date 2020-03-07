# Generated by Django 3.0.2 on 2020-03-05 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='operate_num',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='_event', to='event.OperateNumber'),
        ),
        migrations.AlterField(
            model_name='event',
            name='report_num',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='event', to='event.OperateNumber'),
        ),
    ]
