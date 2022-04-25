from django.db import models

class Type(models.IntegerChoices):
    spot_trade_entropy = 1
    futures_trade_entropy = 2

taskname_map = {
    Type.spot_trade_entropy: '',
    Type.futures_trade_entropy: '',
}
