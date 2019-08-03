
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('degree', '0003_auto_20180503_0840'),
    ]

    operations = [
        migrations.CreateModel(
            name='DegreePlanStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('plan', models.TextField()),
            ],
        ),
    ]
