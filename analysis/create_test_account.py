def main():
    from decimal import Decimal
    from simpletrader.analysis.models import Asset
    from simpletrader.accounts.models import Account, Transaction
    a = Account.objects.create(exchange_id=1, )
    rls = Asset.objects.get(name='rls')
    w = a.get_wallet(rls.id)
    w.create_transaction(
        type=Transaction.Type.subtract_from_free_balance,
        amount=-Decimal('1_000_000_000_0')
    )


main()