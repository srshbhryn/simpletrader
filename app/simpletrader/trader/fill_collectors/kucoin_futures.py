import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpletrader.settings')
django.setup()

import time
import datetime
import logging

from django.db import models as m

from simpletrader.base.utils import GracefulKiller
from simpletrader.trader.models import Account, Fill
from simpletrader.trader.clients import KucoinFutures
from simpletrader.trader.sharedconfigs import Exchange
from simpletrader.trader.tasks import update_order_status_task


log = logging.getLogger('django')


class KucoinFuturesFillCollector(GracefulKiller):

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
        self.client: KucoinFutures = KucoinFutures(token='fill', credentials=self.account.credentials)

    def run(self):
        time_step = datetime.timedelta(days=1)
        first_ts = datetime.datetime.fromtimestamp(time.time()) - time_step
        while self.is_alive:
            try:
                last_fetched_trade_timestamp = self._fills.aggregate(
                    max_timestamp=m.Max('timestamp')
                ).get('max_timestamp') or first_ts
                fills = self.client.get_fills(from_timestamp=last_fetched_trade_timestamp)
                if not fills:
                    first_ts += time_step
                    continue
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
                        exchange_id=Exchange.get_by('name', 'kucoin_futures').id,
                        external_order_id=order_id,
                    )
            except Exception as e:
                log.error(e)
            time.sleep(.5)
