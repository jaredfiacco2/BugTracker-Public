# Generated by Django 2.1.15 on 2020-10-04 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20201004_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactinfo',
            name='Link_DataViz_Embed',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='Link_Github_Embed',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='Link_Linkedin_Embed',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='Link_Website_Embed',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
    ]
