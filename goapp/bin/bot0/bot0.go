package main

import (

	// "goapp/lib/config/markets"

	"fmt"
	"goapp/lib/config"
	"goapp/lib/trader"
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
type OrderResponse struct {
	Code int `json:"code"`
	Id   int `json:"id"`
}

func main() {
	// id, err := trader.PlaceLimitOrder(0, -1, 1, 100, 4000000, true)
	// if err != nil {
	// 	fmt.Println(err)
	// } else {
	// 	fmt.Println("Success placed", id)
	// }
	// time.Sleep(5 * time.Second)
	err := trader.CancelOrder(11)
	if err != nil {
		fmt.Println(err)
	} else {
		fmt.Println("Successfully canceled")
	}
}
