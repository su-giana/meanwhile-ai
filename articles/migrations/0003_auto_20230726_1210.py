# Generated by Django 3.0.5 on 2023-07-26 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20230726_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
