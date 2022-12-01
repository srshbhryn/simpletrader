
from .base import BaseClient


class Dummy(BaseClient):

    is_fake = True
    exchange_id = None

    def __init__(self, token: str) -> None:
        self.token = token

    def place_order(self, params):
        from simpletrader.trader_god.models import DummyOrder
        do = DummyOrder.create(self.exchange_id)
        params['external_id'] = str(do.external_id)
        return params

    def cancel_order(self, external_id):
        from simpletrader.trader_god.models import DummyOrder
        from simpletrader.trader.models import Order
        from simpletrader.trader.sharedconfigs import OrderState
        do = DummyOrder.objects.select_for_update().get(
            external_id=external_id,
        )
        order = Order.objects.select_for_update().get(
            exchange_is=self.exchange_id,
            external_id=external_id,
        )
        assert order.status_id not in [
            OrderState.get_by('name', 'failed_no_fill',).id,
            OrderState.get_by('name', 'canceled_no_fill',).id,
            OrderState.get_by('name', 'canceled_partially_filled',).id,
            OrderState.get_by('name', 'failed_partially_filled',).id,
            OrderState.get_by('name', 'filled',).id,
        ]
        do.delete()
        return None

    def get_order_detail(self, params):
        return params
