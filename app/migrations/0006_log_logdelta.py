# Generated by Django 2.0.4 on 2018-05-24 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_log_logdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='logdelta',
            field=models.IntegerField(null=True),
        ),
    ]
