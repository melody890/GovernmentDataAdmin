# Generated by Django 2.2.3 on 2020-04-11 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20200411_2109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='has_confirmed',
        ),
        migrations.AddField(
            model_name='confirmstring',
            name='password',
            field=models.CharField(default='', max_length=14),
        ),
    ]
