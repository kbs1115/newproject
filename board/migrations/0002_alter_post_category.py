# Generated by Django 4.0.6 on 2023-01-01 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.TextField(default=20),
        ),
    ]