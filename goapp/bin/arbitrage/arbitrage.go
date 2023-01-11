package main

import (
	"fmt"
	"goapp/lib/arbitrage"
	"goapp/lib/bookwatch"
	"goapp/lib/config"
	"goapp/lib/trader"
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
