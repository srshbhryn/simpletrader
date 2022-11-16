package main

import (
	"fmt"
	"goapp/lib/bookwatch"
	"goapp/lib/config"
	"goapp/lib/config/assets"
	"goapp/lib/config/exchanges"
	"goapp/lib/config/markets"
	"goapp/lib/trader"
)

func init() {
	trader.Load()
	config.Load()
	bookwatch.Load()
}

func main() {
	baseAssetId := assets.ByName("usdt").Id
	quoteAssetId := assets.ByName("rls").Id
	exchangeId := exchanges.ByName("nobitex").Id
	market, err := markets.GetByAssetsAndExchange(baseAssetId, quoteAssetId, exchangeId)
	if err != nil {
		panic(err)
	}
	// for {
	book, err := bookwatch.ReadBook(market.Id)
	if err != nil {
		panic(err)
	}
	fmt.Println(book.BestAskPrice, book.BestBidPrice)
	orderId, err := trader.PlaceLimitOrder(baseAssetId, quoteAssetId, exchangeId, 30, (book.BestBidPrice), false)
	if err != nil {
		panic(err)
	}
	fmt.Println("SUCCESS", orderId)
	// time.Sleep(100 * time.Millisecond)
	// }

}
