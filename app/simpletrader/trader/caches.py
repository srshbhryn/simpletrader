from typing import Dict, Tuple

from .models import Bot, Account, BotAccount


class BotCache:
    _bots: Dict[str, Bot] = {}

    @classmethod
    def get(cls, token: str):
        if not token in cls._bots:
            cls._bots[token] = Bot.objects.get(token=token)
        return cls._bots[token]
