# Generated by Django 3.2.16 on 2023-02-10 14:28

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import timescale.db.models.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('analysis', '0004_orderstatus'),
        ('accounts', '0004_auto_20230210_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('external_id', models.CharField(db_index=True, max_length=32)),
                ('client_order_id', models.CharField(db_index=True, default=None, max_length=128, null=True)),
                ('leverage', models.SmallIntegerField(default=1)),
                ('timestamp', timescale.db.models.fields.TimescaleDateTimeField(default=django.utils.timezone.now, interval='24 hour')),
                ('price', models.DecimalField(decimal_places=16, default=None, max_digits=32, null=True)),
                ('volume', models.DecimalField(decimal_places=16, max_digits=32)),
                ('is_sell', models.BooleanField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.account')),
                ('exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.exchange')),
                ('pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.pair')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.orderstatus')),
            ],
        ),
        migrations.CreateModel(
            name='Fill',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('external_id', models.CharField(db_index=True, max_length=32)),
                ('external_order_id', models.CharField(db_index=True, max_length=32)),
                ('timestamp', timescale.db.models.fields.TimescaleDateTimeField(default=django.utils.timezone.now, interval='24 hour')),
                ('price', models.DecimalField(decimal_places=16, default=None, max_digits=32, null=True)),
                ('volume', models.DecimalField(decimal_places=16, max_digits=32)),
                ('is_sell', models.BooleanField()),
                ('fee', models.DecimalField(decimal_places=16, max_digits=32)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.account')),
                ('exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.exchange')),
                ('fee_asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.asset')),
                ('pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.pair')),
            ],
        ),
    ]
