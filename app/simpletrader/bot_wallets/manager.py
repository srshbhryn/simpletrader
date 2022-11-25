import decimal

from simpletrader.trader.models import Bot

from .models import Wallet, WalletTransaction

class BotWalletManager:
    TRANSACTION_TYPES = WalletTransaction.Types

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.wallets = {}

    def _get_wallet(self, asset_id: int) -> Wallet:
        wallet = self.wallets.get(asset_id)
        if wallet is not None:
            return wallet
        wallet = Wallet.objects.get(
            bot=self.bot,
            asset_id=asset_id,
        )
        self.wallets[asset_id] = wallet
        return wallet

    def create_transaction(self,
        asset_id: int,
        amount: decimal.Decimal,
        type: int,
    ) -> None:
        wallet = self._get_wallet(asset_id)
        wallet.create_transaction(
            amount=amount,
            type=type,
        )
