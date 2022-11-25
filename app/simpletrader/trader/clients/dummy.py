
from .base import BaseClient


class Dummy(BaseClient):
    def __init__(self, token: str) -> None:
        self.token = token

    def place_order(self, *args, **kwargs):
        pass

    def cancel_order(self, *args, **kwargs):
        pass

    def get_order_detail(self, *args, **kwargs):
        pass
