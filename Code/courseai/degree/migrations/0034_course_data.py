# Generated by Django 2.1.1 on 2018-10-07 15:26

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('degree', '0033_auto_20181007_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=''),
            preserve_default=False,
        ),
    ]