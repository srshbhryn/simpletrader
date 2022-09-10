def main():
    from simpletrader.trader.models import Bot
    from simpletrader.trader.sharedconfigs import Exchange
    bot = Bot.objects.first()
    print(vars(bot))
    client = bot.get_client(Exchange.get_by('name', 'nobitex').id)
    print(vars(client))
    fills = client.get_fills()
    print(fills)



main()
