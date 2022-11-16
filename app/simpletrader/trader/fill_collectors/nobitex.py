import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpletrader.settings')
django.setup()

import time
import logging

from django.db import models as m

from simpletrader.base.utils import GracefulKiller
from simpletrader.trader.models import Account, Fill
from simpletrader.trader.clients import Nobitex
from simpletrader.trader.sharedconfigs import Exchange
from simpletrader.trader.tasks import update_order_status_task


log = logging.getLogger('django')

class NobitexFillCollector(GracefulKiller):

    @classmethod
    def create_and_run(cls, account_id):
        i = cls(account_id)
        i._init()
        i.run()

    def __init__(self, account_id) -> None:
        self.account_id = account_id
        self.account: Account = None
        super().__init__()

    @property
    def _fills(self):
        return Fill.objects.filter(account_id=self.account_id)

    def _init(self):
        self.account: Account = Account.objects.get(pk=self.account_id)
        self.client: Nobitex = Nobitex(token='fill', credentials=self.account.credentials)

    def run(self):
        while self.is_alive:
            try:
                last_fetched_id = self._fills.aggregate(
                    max_id=m.Max('external_id')
                ).get('max_id') or -1
                fills = self.client.get_fills(from_id=int(last_fetched_id)+1)
                Fill.objects.bulk_create([
                    Fill(**{
                        'account_id': self.account_id,
                        **fill
                    })
                    for fill in fills
                ], batch_size=100)
                order_ids = set([
                    fill['external_order_id']
                    for fill in fills
                ])
                for order_id in order_ids:
                    update_order_status_task.delay(
                        exchange_id=Exchange.get_by('name', 'nobitex').id,
                        external_order_id=order_id,
                    )
            except Exception as e:
                log.error(e)
            time.sleep(60/20)
