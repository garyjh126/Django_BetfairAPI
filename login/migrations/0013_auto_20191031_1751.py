# Generated by Django 2.2.6 on 2019-10-31 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0012_auto_20191031_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketdictionarym',
            name='market_removed',
            field=models.BooleanField(default=False, max_length=50),
        ),
    ]
