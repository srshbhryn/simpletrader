# Generated by Django 3.2.5 on 2022-12-01 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0002_auto_20221201_1617'),
        ('bot_wallets', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='wallet',
            name='unqibotassetexchange',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='bot',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='exchange_id',
        ),
        migrations.AddField(
            model_name='wallet',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='trader.account'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='wallet',
            constraint=models.UniqueConstraint(fields=('account_id', 'asset_id'), name='unqibotassetexchange'),
        ),
    ]
