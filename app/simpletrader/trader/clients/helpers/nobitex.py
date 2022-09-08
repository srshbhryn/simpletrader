from typing import TypedDict


class Currencies(TypedDict):
    nbx_name: str
    asset_name: str

_currencies: Currencies = {}

for _, nbx_currency, translation in [
    (0, 'unknown', 'unknown'),
    (1, 'usd', 'USD'),
    (2, 'rls', '﷼'),
    (10, 'btc', 'Bitcoin'),
    (11, 'eth', 'Ethereum'),
    (12, 'ltc', 'Litecoin'),
    (13, 'usdt', 'Tether'),
    (14, 'xrp', 'Ripple'),
    (15, 'bch', 'BitcoinCash'),
    (16, 'bnb', 'BinanceCoin'),
    (17, 'eos', 'EOS'),
    (18, 'doge', 'Dogecoin'),
    (19, 'xlm', 'Stellar'),
    (20, 'trx', 'TRON'),
    (21, 'ada', 'Cardano'),
    (22, 'xmr', 'Monero'),
    (23, 'xem', 'NEM'),
    (24, 'iota', 'IOTA'),
    (25, 'etc', 'EthereumClassic'),
    (26, 'dash', 'Dash'),
    (27, 'zec', 'Zcash'),
    (28, 'neo', 'Neo'),
    (29, 'qtum', 'Qtum'),
    (30, 'xtz', 'Tezos'),
    (31, 'pmn', 'Paymon'),
    (32, 'link', 'Chainlink'),
    (33, 'dai', 'Dai'),
    (34, 'dot', 'Polkadot'),
    (35, 'uni', 'Uniswap'),
    (36, 'aave', 'Aave'),
    (37, 'sol', 'Solana'),
    (38, 'matic', 'Matic'),
    (39, 'fil', 'Filecoin'),
    (40, 'grt', 'Graph'),
    (41, 'theta', 'Theta'),
    (42, 'shib', '1000SHIB'),
    # Xchange coins
    (50, 'inch', '1inch'),
    (51, 'alice', 'MyNeighborAlice'),
    (52, 'alpha', 'AlphaFinanceLab'),
    (53, 'ankr', 'Ankr'),
    (54, 'arpa', 'ARPAChain'),
    (55, 'ata', 'Automata'),
    (56, 'atom', 'Cosmos'),
    (57, 'avax', 'Avalanche'),
    (58, 'axs', 'Axie'),
    (59, 'bake', 'BakeryToken'),
    (60, 'bal', 'Balancer'),
    (61, 'band', 'BAND'),
    (62, 'bat', 'BasicAttentionToken'),
    (63, 'bel', 'BellaProtocol'),
    (64, 'blz', 'Bluzelle'),
    (65, 'btt', 'BitTorrent'),
    (66, 'c98', 'Coin98'),
    (67, 'celr', 'CelerNetwork'),
    (68, 'chr', 'Chromia'),
    (69, 'comp', 'Compound'),
    (70, 'coti', 'COTI'),
    (71, 'ctk', 'CertiK'),
    (72, 'ctsi', 'Cartesi'),
    (73, 'dodo', 'DODO'),
    (74, 'egld', 'ElrondEGold'),
    (75, 'ftm', 'Fantom'),
    (76, 'gala', 'Gala'),
    (77, 'iotx', 'IoTeX'),
    (78, 'knc', 'KyberNetwork'),
    (79, 'ksm', 'Kusama'),
    (80, 'lina', 'Linear'),
    (81, 'lit', 'Litentry'),
    (82, 'mask', 'MaskNetwork'),
    (83, 'mkr', 'Maker'),
    (84, 'near', 'NEARProtocol'),
    (85, 'ocean', 'OceanProtocol'),
    (86, 'ont', 'Ontology'),
    (87, 'reef', 'ReefFinance'),
    (88, 'sfp', 'SafePal'),
    (89, 'snx', 'SynthetixNetworkToken'),
    (90, 'sushi', 'Sushi'),
    (91, 'sxp', 'Swipe'),
    (92, 'tlm', 'AlienWorlds'),
    (93, 'unfi', 'UnifiProtocolDAO'),
    (94, 'yfi', 'yearn.finance'),
    (95, 'yfii', 'DFI.Money'),
    (96, 'zil', 'Zilliqa'),
    (97, 'mana', 'Mana'),
    (98, 'sand', 'Sand'),
    (99, 'ape', 'ApeCoin'),
    (100, 'one', 'Harmony'),
    (101, 'wbtc', 'WrappedBitcoin'),
    (102, 'usdc', 'USDCoin'),
    (103, 'algo', 'Algorand'),
    (104, 'luna', 'Terra'),
    (105, 'klay', 'Klaytn'),
    (106, 'gmt', 'STEPN'),
    (107, 'chz', 'Chiliz'),
    (108, 'vet', 'VeChain'),
    (109, 'qnt', 'Quant'),
]:
    _currencies[translation] = nbx_currency

def translate_currency(nbx_name: str) -> str:
    return _currencies[nbx_name]


class OrderStates(TypedDict):
    nbx_name: str
    name: str


_order_states: OrderStates = {}

for name, nbx_name in [
    ('placed', 'New'),
    ('placed', 'Active'),
    ('filled', 'Done'),
    ('cancelled', 'Canceled'),
]:
    _order_states[nbx_name] = name



def translate_order_status(nbx_name: str) -> str:
    return _order_states[nbx_name]
