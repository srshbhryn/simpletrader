

class BaseClient:
    def __init__(self, token, credentials) -> None:
        raise NotImplementedError()

    def place_order(self, amount, price, ) -> None:
        raise NotImplementedError()

    def cancel_order(self, amount, price, ) -> None:
        raise NotImplementedError()

    def get_order_status(self, amount, price, ) -> None:
        raise NotImplementedError()
