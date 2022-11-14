package main

import (
	"fmt"
	"goapp/lib/arbitrage"
	"goapp/lib/bookwatch"
	"goapp/lib/config"
	"goapp/lib/trader"
	"math/rand"
	"sync"

	"golang.org/x/sync/errgroup"
)

func init() {
	trader.Load()
	config.Load()
	bookwatch.Load()
}

func main() {
	var s sync.Mutex
	var condition sync.Cond
	a := errgroup.Group()
	a.

	// condition.
	// errgroup.
	go func ()  {
		r := rand.Intn(2)
		fmt.Println(r)
		if r == 0 {
			s.Lock()
		}
	}()
	// for _, mp := range arbitrage.GetKucoinArbitrageMarkets() {
	// 	fmt.Println(mp)
	// 	fmt.Println(mp.NobitexMarket.Symbol)
	// 	fmt.Println(mp.KucoinMarket.Symbol)
	}
	// kucoinArbitrageSearch()
	// // bookwatch.ExampleClient()
	// market, err := markets.GetByAssetsAndExchange(assets.ByName("usdt").Id, assets.ByName("rls").Id, exchanges.ByName("nobitex").Id)
	// if err != nil {
	// 	panic(err)
	// }
	// fee := float64((1 / 100) / 10)
	// feeFactor := (1 - fee)
	// gainFactor := feeFactor * feeFactor
	// for {
	// 	b, err := bookwatch.ReadBook(market.Id)
	// 	fmt.Println(b)
	// 	if err != nil {
	// 		panic(err)
	// 	}
	// 	fmt.Println(gainFactor * b.BestAskPrice / b.BestBidPrice)
	// 	time.Sleep(time.Second)
	// }
	// // id, err := trader.PlaceLimitOrder(0, -1, 1, 100, 4000000, true)
	// // if err != nil {
	// // 	fmt.Println(err)
	// // } else {
	// // 	fmt.Println("Success placed", id)
	// // }
	// // time.Sleep(5 * time.Second)
	// err = trader.CancelOrder(id)
	// // err := trader.CancelOrder(14)
	// if err != nil {
	// 	fmt.Println(err)
	// } else {
	// 	fmt.Println("Successfully canceled")
	// }
}
