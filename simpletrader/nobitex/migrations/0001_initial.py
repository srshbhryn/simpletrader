# Generated by Django 3.2.5 on 2022-05-20 20:36

from django.db import migrations, models
import django.db.models.deletion
import timescale.db.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_asset', models.CharField(max_length=8)),
                ('quote_asset', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', timescale.db.models.fields.TimescaleDateTimeField(interval='1 hour')),
                ('price', models.FloatField()),
                ('volume', models.FloatField()),
                ('is_buyer_maker', models.BooleanField()),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nobitex.market')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', timescale.db.models.fields.TimescaleDateTimeField(interval='6 hour')),
                ('price', models.FloatField()),
                ('volume', models.FloatField()),
                ('is_bid', models.BooleanField()),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nobitex.market')),
            ],
        ),
    ]
