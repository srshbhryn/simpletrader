# Generated by Django 3.2.5 on 2021-07-22 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nobitex', '0002_alter_markettrades_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='markettrades',
            name='time',
            field=models.PositiveBigIntegerField(),
        ),
    ]