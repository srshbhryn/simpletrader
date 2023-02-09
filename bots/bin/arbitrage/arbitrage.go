package main

import (
	"bots/lib/arbitrage"
	"bots/lib/bookwatch"
	"bots/lib/config"
	"bots/lib/trader"
	"fmt"
)

func init() {
	trader.Load()
	config.Load()
	bookwatch.Load()
}

func main() {
	pairs := arbitrage.GetKucoinArbitrageMarkets()
	for {
		for _, pair := range pairs {
			for _, isSell := range []bool{true, false} {
				amount, err := pair.GetAmount(isSell)
				if err != nil {
					continue
				}
				fmt.Println(pair.NobitexMarket.Symbol, "\t", amount)
			}
		}
	}
}
