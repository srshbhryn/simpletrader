import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpletrader.settings')
django.setup()

import time
import logging

from django.db import models as m

from simpletrader.base.utils import GracefulKiller
from simpletrader.trader.models import Account, WalletSnapShot
from simpletrader.trader.clients import KucoinFutures

log = logging.getLogger('django')

class KucoinFuturesBalanceCollector(GracefulKiller):

    @classmethod
    def create_and_run(cls, account_id):
        i = cls(account_id)
        i._init()
        i.run()

    def __init__(self, account_id) -> None:
        self.account_id = account_id
        self.account: Account = None
        super().__init__()

    def _init(self):
        self.account: Account = Account.objects.get(pk=self.account_id)
        self.client: KucoinFutures = KucoinFutures(credentials=self.account.credentials, token='blnc')

    def run(self):
        while self.is_alive:
            try:
                WalletSnapShot.objects.create(**{
                    'account_id': self.account_id,
                    **self.client.get_usdt_balances()
                })
                WalletSnapShot.objects.bulk_create([
                    WalletSnapShot(**{
                        'account_id': self.account_id,
                        **wallet_balance
                    })
                    for wallet_balance in self.client.get_positions()
                ],batch_size=100)
            except Exception as e:
                log.error(e)
            time.sleep(1)
