# Generated by Django 2.1.15 on 2020-10-06 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_usecases'),
    ]

    operations = [
        migrations.AddField(
            model_name='usecases',
            name='Active',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
