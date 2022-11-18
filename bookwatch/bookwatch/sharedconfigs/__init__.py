import os
import json

CONFIG_DIR = os.environ.get('CONFIG_DIR')

class Base:

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if not k in self.__class__.instances:
                self.__class__.instances[k] = {}
            if not v in self.__class__.instances[k]:
                self.__class__.instances[k][v] = []
            self.__class__.instances[k][v].append(self)

    @classmethod
    def get_by(cls, key: str,  value) -> 'Base':
        instances = cls.instances.get(key)
        if not instances:
            return None
        instances = instances.get(value)
        if not instances:
            return None
        if len(instances) == 1:
            return instances[0]
        return instances


class Asset(Base):
    instances = {}

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name
        super().__init__(id=id, name=name)

class Exchange(Base):
    instances = {}

    def __init__(self, id: int, name: str, taker_fee: float, maker_fee: float) -> None:
        self.id = id
        self.name = name
        self.taker_fee = taker_fee
        self.maker_fee = maker_fee
        super().__init__(id=id, name=name)

class Market(Base):
    instances = {}

    def __init__(
        self,
        id: int,
        base_asset_id: int,
        quote_asset_id: int,
        exchange_id: int,
        symbol: str,
    ) -> None:
        self.id: int = id
        self.base_asset: Asset = Asset.get_by('id', base_asset_id)
        self.quote_asset: Asset = Asset.get_by('id', quote_asset_id)
        self.exchange: Exchange = Exchange.get_by('id', exchange_id)
        self.symbol: str = symbol
        super().__init__(id=id, symbol=symbol,)

class OrderState(Base):
    instances = {}
    def __init__(
        self,
        id: int,
        name: str,
    ) -> None:
        self.id = id
        self.name = name
        super().__init__(id=id, name=name)

with open(f'{CONFIG_DIR}assets.json') as f:
    ASSETS = [
        Asset(**a)
        for a in json.load(f)
    ]

with open(f'{CONFIG_DIR}exchanges.json') as f:
    EXCHANGES = [
        Exchange(**a)
        for a in json.load(f)
    ]

with open(f'{CONFIG_DIR}markets.json') as f:
    MARKETS = [
        Market(**a)
        for a in json.load(f)
    ]

with open(f'{CONFIG_DIR}order_states.json') as f:
    ORDER_STATES = [
        OrderState(**a)
        for a in json.load(f)
    ]
