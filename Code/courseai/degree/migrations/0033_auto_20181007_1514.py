# Generated by Django 2.1.1 on 2018-10-07 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('degree', '0032_auto_20181007_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='degreerequirement',
            name='name',
            field=models.TextField(blank=True, default='', editable=False),
        ),
    ]