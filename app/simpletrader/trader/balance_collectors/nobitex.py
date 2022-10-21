import time
import logging

from django.db import models as m

from simpletrader.base.utils import GracefulKiller
from simpletrader.trader.models import Account, WalletSnapShot
from simpletrader.trader.clients import Nobitex

log = logging.getLogger('django')

class NobitexBalanceCollector(GracefulKiller):

    @classmethod
    def create_and_run(cls, account_id):
        i = cls(account_id)
        i.run()

    def __init__(self, account_id) -> None:
        self.account_id = account_id
        self.account: Account = None
        super().__init__()


    def _init(self):
        self.account: Account = Account.objects.get(pk=self.account_id)
        self.client: Nobitex = Nobitex(credentials=self.account.credentials)

    def run(self):
        while self.is_alive:
            try:
                WalletSnapShot.objects.bulk_create([
                    WalletSnapShot(**{
                        'account_id': self.account_id,
                        **wallet_balance
                    })
                    for wallet_balance in self.client.get_balances()
                ],)
            except Exception as e:
                log.error(e)
            time.sleep(2)
