# Generated by Django 2.0.4 on 2018-04-19 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('requirements', models.TextField()),
            ],
        ),
    ]