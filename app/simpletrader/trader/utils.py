import functools

from simpletrader.trader.sharedconfigs import OrderState


@functools.cache
def final_order_state_ids():
    return [
        OrderState.get_by('name', state_name).id
        for state_name in [
            'failed_no_fill',
            'canceled_no_fill',
            'canceled_partially_filled',
            'failed_partially_filled',
            'filled',
        ]
    ]


@functools.cache
def open_order_state_ids():
    return [
        OrderState.get_by('name', state_name).id
        for state_name in [
            'queued',
            'open_no_fill',
            'open_partially_filled',
        ]
