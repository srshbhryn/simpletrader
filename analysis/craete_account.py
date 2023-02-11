def main():
    from simpletrader.accounts.models import Account
    a = Account.objects.create(exchange_id=1)
    print(a)

main()