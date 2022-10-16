import time
import logging

from django.db import models as m

from simpletrader.base.utils import GracefulKiller
from simpletrader.trader.models import Account, Fill
from simpletrader.trader.clients import Nobitex

log = logging.getLogger('django')

class NobitexFillCollector(GracefulKiller):

    @classmethod
    def create_and_run(cls, account_id):
        i = cls(account_id)
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
        self.client: Nobitex = Nobitex(credentials=self.account.credentials)

    def exit_gracefully(self, *args, **kwargs):
        return super().exit_gracefully(*args, **kwargs)

    def run(self):
        while self.is_alive:
            try:
                last_fetched_id = self._fills.aggregate(
                    max_id=m.Max('external_id')
                ).get('max_id') or -1
                Fill.objects.bulk_create([
                    Fill(**{
                        'account_id': self.account_id,
                        **fill
                    })
                    for fill in self.client.get_fills(from_id=last_fetched_id+1)
                ], batch_size=100)
            except Exception as e:
                log.error(e)
            time.sleep(2)
