import random

from kucoin.client import Market as SpotMarket
from kucoin_futures.client import Market as FuturesMarket

# General keys should be from diffrent accounts in order to
# mitigate API restrictions.
spot_general_keys = ['61e5a987a2cd6f0001937b4f', ]
spot_general_secrets = ['1639b074-31df-4a3f-87d6-9286c6ed4868', ]
spot_general_passphrases = ['akdo2ui3gb2983g', ]

futures_general_keys = ['61e5d271d91d2d00012e4e24', ]
futures_general_secrets = ['5104cc15-d870-4870-b823-dc3630809066', ]
futures_general_passphrases = ['2NmJs7y!Si64aBv', ]


spot_clients = [
    SpotMarket(
        key=spot_general_keys[i%len(spot_general_keys)],
        secret=spot_general_secrets[i%len(spot_general_keys)],
        passphrase=spot_general_passphrases[i%len(spot_general_keys)],
    )
    for i in range(100*len(spot_general_keys))
]


futures_clients = [
    FuturesMarket(
        key=futures_general_keys[i%len(futures_general_keys)],
        secret=futures_general_secrets[i%len(futures_general_keys)],
        passphrase=futures_general_passphrases[i%len(futures_general_keys)],
    )
    for i in range(100*len(spot_general_keys))
]


def get_spot_client():
    return random.choice(spot_clients)


def get_futures_client():
    return random.choice(futures_clients)
