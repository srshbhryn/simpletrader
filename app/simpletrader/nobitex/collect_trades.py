import logging
import time

from simpletrader.base.models import Exchange
from simpletrader.kucoin.models import Market
from simpletrader.nobitex.client import get_client
from simpletrader.nobitex.journals import TradeJournal
from simpletrader.nobitex.models import Market as NbxMarket

logger = logging.getLogger('django')


class TradeCollector:
    def __init__(self):
        pass

    def _initialize(self):
        self.client = get_client()
        self.nbx_market_id_to_market_id_maps = { #nobitex market to general market
            m.related_id: m.id
            for m in Market.objects.filter(type=Exchange.nobitex)
        }
        self.nbx_market_id_to_symbol_map = { #nobitex market to symbol
            m.id: m.symbol.upper()
            for m in NbxMarket.objects.all()
            if m.id in self.nbx_market_id_to_market_id_maps
        }
        self.client = get_client()
        self.journal = TradeJournal()


    def run(self):
        sleep_time = 5 / len(self.nbx_market_id_to_market_id_maps)
        for nmid in self.nbx_market_id_to_market_id_maps:
            try:
                self.collect_trades(nmid)
            except Exception as e:
                logger.info(e)
            time.sleep(sleep_time)

    def _serialize_trade(self, obj):
        price_parts = str(obj['price']).split('.')
        if len(price_parts) == 0:
            price_parts.append(['0'])
        if len(price_parts[0]) < 10:
            price_parts[0] = price_parts[0] + (10 - len(price_parts[0])) * '0'
        if len(price_parts[1]) < 10:
            price_parts[1] = (10 - len(price_parts[1])) * '0' + price_parts[1]
        sort_field = str(obj['time']) + (
            '0' if obj['is_buy'] else '1'
        ) + price_parts[1] + price_parts[0]
        return({
            'market_id': obj['market_id'],
            'time': obj['time'],
            'sort_field': sort_field,
            'price': obj['price'],
            'volume': obj['volume'],
            'is_buyer_maker': obj['is_buy'],
        })

    def collect_trades(self, nbx_market_id):
        symbol = self.nbx_market_id_to_symbol_map[nbx_market_id]
        response = self.client.get_trades(symbol)
        mid = self.nbx_market_id_to_market_id_maps[nbx_market_id]
        for trade in response['trades']:
            trade['market_id'] = mid
            self.journal.append_line(self._serialize_trade(trade))
