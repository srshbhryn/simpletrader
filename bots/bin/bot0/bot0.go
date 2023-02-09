package main

import (
	"bots/lib/bookwatch"
	"bots/lib/config"
	"bots/lib/config/assets"
	"bots/lib/config/exchanges"
	"bots/lib/config/markets"
	"bots/lib/trader"
	"fmt"
	"time"
)

func init() {
	trader.Load()
	config.Load()
	bookwatch.Load()
}

func checkBookDelay() {
	nobitexMarket, err := markets.GetByAssetsAndExchange(
		assets.ByName("usdt").Id,
		assets.ByName("rls").Id,
		exchanges.ByName("nobitex").Id,
	)
	kucoinMarket, err := markets.GetByAssetsAndExchange(
		assets.ByName("btc").Id,
		assets.ByName("usdt").Id,
		exchanges.ByName("kucoin_futures").Id,
	)

	if err != nil {
		panic(err)
	}
	for {
		nobitexBook, err := bookwatch.ReadBook(nobitexMarket.Id)
		if err != nil {
			panic(err)
		}
		kucoinBook, err := bookwatch.ReadBook(kucoinMarket.Id)
		if err != nil {
			panic(err)
		}
		now := time.Now()
		fmt.Println(now.Sub(nobitexBook.Timestamp), "\t", now.Sub(kucoinBook.Timestamp))
		time.Sleep(100 * time.Microsecond)
	}
}

func placeOrder() {
	// checkBookDelay()
	baseAssetId := assets.ByName("usdt").Id
	quoteAssetId := assets.ByName("rls").Id
	exchangeId := exchanges.ByName("nobitex").Id
	market, err := markets.GetByAssetsAndExchange(baseAssetId, quoteAssetId, exchangeId)
	if err != nil {
		panic(err)
	}
	book, err := bookwatch.ReadBook(market.Id)
	if err != nil {
		panic(err)
	}
	fmt.Println(book.BestAskPrice, book.BestBidPrice)
	orderId, err := trader.PlaceLimitOrder(baseAssetId, quoteAssetId, exchangeId, 10, (book.BestBidPrice), true)
	if err != nil {
		panic(err)
	}
	fmt.Println("SUCCESS", orderId)
	for {
		stat, filledAmount, err := trader.GetOrderStatusAndFills(orderId)
		if err != nil {
			panic(err)
		}
		fmt.Println(stat)
		fmt.Println(filledAmount)
	}
	// time.Sleep(100 * time.Millisecond)
	// }

}

func getWalletsStats() {
	baseAssetId := assets.ByName("usdt").Id
	quoteAssetId := assets.ByName("rls").Id
	exchangeId := exchanges.ByName("nobitex").Id
	fmt.Println(trader.GetWalletsStats(baseAssetId, exchangeId))
	fmt.Println(trader.GetWalletsStats(quoteAssetId, exchangeId))
}

func placeKucoinOrder() {
	baseAssetId := assets.ByName("eth").Id
	quoteAssetId := assets.ByName("usdt").Id
	exchangeId := exchanges.ByName("kucoin_futures").Id
	market, err := markets.GetByAssetsAndExchange(baseAssetId, quoteAssetId, exchangeId)
	if err != nil {
		panic(err)
	}
	book, err := bookwatch.ReadBook(market.Id)
	if err != nil {
		panic(err)
	}
	fmt.Println(book.BestAskPrice, book.BestBidPrice)
	orderId, err := trader.PlaceLimitOrder(baseAssetId, quoteAssetId, exchangeId, .03, (book.BestAskPrice)*.9, false)
	if err != nil {
		panic(err)
	}
	fmt.Println("SUCCESS", orderId)
	// time.Sleep(time.Second)
	// err = trader.CancelOrder(orderId)
	// if err != nil {
	// 	panic(err)
	// }
	// fmt.Println("CANCELED")
	for {
		stat, filledAmount, err := trader.GetOrderStatusAndFills(orderId)
		if err != nil {
			panic(err)
		}
		fmt.Println(stat)
		fmt.Println(filledAmount)
	}
}

func getKucoinBalance() {
	quoteAssetId := assets.ByName("usdt").Id
	exchangeId := exchanges.ByName("kucoin_futures").Id
	stats, err := trader.GetWalletsStats(quoteAssetId, exchangeId)
	if err != nil {
		panic(err)
	}
	fmt.Println(stats)
	baseAssetId := assets.ByName("eth").Id
	stats, err = trader.GetWalletsStats(baseAssetId, exchangeId)
	if err != nil {
		panic(err)
	}
	fmt.Println(stats)

}
func main() {
	// getKucoinBalance()
	checkBookDelay()
	// placeKucoinOrder()
}