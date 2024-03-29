# Generated by Django 3.2.16 on 2023-02-10 08:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import timescale.db.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.URLField()),
                ('description', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('free_balance', models.DecimalField(decimal_places=16, default=0, max_digits=32)),
                ('blocked_balance', models.DecimalField(decimal_places=16, default=0, max_digits=32)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.account')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.asset')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, serialize=False)),
                ('created_at', timescale.db.models.fields.TimescaleDateTimeField(default=django.utils.timezone.now, interval='10 day')),
                ('type', models.SmallIntegerField(choices=[(10, 'Add To Blocked Balance'), (11, 'Subtract From Free Balance'), (30, 'Block')])),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.wallet')),
            ],
        ),
        migrations.AddConstraint(
            model_name='wallet',
            constraint=models.UniqueConstraint(fields=('account', 'asset'), name='unique_bot_asset_pair'),
        ),
        migrations.AddConstraint(
            model_name='wallet',
            constraint=models.CheckConstraint(check=models.Q(('free_balance__gte', 0)), name='non_negative_free_balance'),
        ),
        migrations.AddConstraint(
            model_name='wallet',
            constraint=models.CheckConstraint(check=models.Q(('blocked_balance__gte', 0)), name='non_negative_block_balance'),
        ),
    ]
