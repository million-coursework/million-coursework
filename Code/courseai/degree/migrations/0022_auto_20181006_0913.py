# Generated by Django 2.1.1 on 2018-10-06 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('degree', '0021_auto_20181006_0759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='es_id',
            field=models.CharField(default='', editable=False, max_length=10),
        ),
    ]