# Generated by Django 2.2.6 on 2019-10-10 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_auto_20191001_1711'),
    ]

    operations = [
        migrations.CreateModel(
            name='SportsAPI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payload', models.CharField(max_length=400)),
                ('url', models.CharField(max_length=100)),
                ('headers', models.CharField(max_length=200)),
                ('path_cert', models.CharField(max_length=200)),
            ],
        ),
    ]