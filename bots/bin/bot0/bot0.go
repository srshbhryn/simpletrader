package main

import (
	"bots/bin/bot0/bot0"
	"bots/lib/bookwatch"
	"bots/lib/config/exchanges"
	"bots/lib/config/markets"
	"bots/lib/rpc"
	"bots/lib/rpc/trade"
	"time"
)

func main() {
	rpc.Load()
	bookwatch.Load()
	accountUUID, err := trade.GetDemoAccount(exchanges.Nobitex)
	if err != nil {
		panic(err)
	}
	trade.SetAccountUUID(accountUUID)
	conf := bot0.SimpleBotConfig{
		Market:                       markets.NobitexUsdtRls,
		TimeDelta:                    5 * time.Minute,
		Len:                          3,
		PriceRoundingPrecision:       100.0,
		TradeSize:                    40,
		StopLossRatio:                0,
		GainRatio:                    1.0025,
		MinBaseBalance:               700,
		MinQuoteBalance:              0,
		ErrorHandler:                 func(err error) { panic(err) },
		CheckInterval:                time.Minute,
		SideSleepAfterOrderPlacement: 10 * time.Minute,
	}
	bot := bot0.New(&conf)
	bot.Run()
	time.Sleep(time.Hour)
}
