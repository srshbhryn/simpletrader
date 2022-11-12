package main

import (
	"encoding/json"
	"errors"
	"fmt"

	// "goapp/lib/config/markets"

	"goapp/lib/config"
	"goapp/lib/config/markets"
	"goapp/lib/trader"
	"time"

	"github.com/srshbhryn/gocelery"
)

func init() {
	trader.Load()
	config.Load()
}

type OrderParams struct {
	BotToken   string   `json:"bot_token"`
	ExchangeId int      `json:"exchange_id"`
	MarketId   int      `json:"market_id"`
	StatusId   int      `json:"status_id"`
	Leverage   *int     `json:"leverage"`
	Price      *float64 `json:"price"`
	Volume     float64  `json:"volume"`
	IsSell     bool     `json:"is_sell"`
}

func main() {
	market, err := markets.GetByAssetsAndExchange(2, 0, 1)
	if err != nil {
		panic(err)
	}
	args, err := json.Marshal(
		OrderParams{
			BotToken:   "test",
			ExchangeId: 1,
			MarketId:   market.Id,
			// MarketId:   2,
			Volume: 0.01,
			// Leverage: &a,
			IsSell: true,
		})
	if err != nil {
		panic(err)
	}
	// for {
	response, err := trader.Call("trader.place_order", string(args))
	if err != nil {
		fmt.Println(err)
		if errors.Is(err, gocelery.TaskFailedError) {
			fmt.Println("AAAAAAAAAAAA")
			panic(":(")
		}
		// fmt.Println("error")
	}
	fmt.Println("--------")
	fmt.Println(response)
	time.Sleep(10 * time.Second)
	// }/
}
