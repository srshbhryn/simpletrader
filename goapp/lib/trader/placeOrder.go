package trader

import (
	"encoding/json"
	"fmt"
	"goapp/lib/config"
	"goapp/lib/config/markets"
)

type OrderId int

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

func PlaceMarketOrder(
	baseAssetId int,
	quoteAssetId int,
	exchangeId int,
	amount float64,
	isSell bool,
) (OrderId, error) {
	market, err := markets.GetByAssetsAndExchange(baseAssetId, quoteAssetId, exchangeId)
	if err != nil {
		return 0, err
	}
	args, err := json.Marshal(OrderParams{
		BotToken:   config.BotToken,
		Leverage:   config.DefaultLeverage,
		ExchangeId: exchangeId,
		MarketId:   market.Id,
		Volume:     amount,
		IsSell:     isSell,
	})
	if err != nil {
		return 0, err
	}
	responseBody, err := call("trader.place_order", string(args))
	if err != nil {
		return 0, err
	}
	responseBodyString, _ := responseBody.(string)
	response := OrderResponse{}
	err = json.Unmarshal([]byte(responseBodyString), &response)
	if err != nil {
		return 0, err
	}
	if response.Code != 0 {
		return 0, fmt.Errorf("OrderPlaceMentFailed:code:%d", response.Code)
	}
	return OrderId(response.Id), nil
}

func PlaceLimitOrder(
	baseAssetId int,
	quoteAssetId int,
	exchangeId int,
	amount float64,
	price float64,
	isSell bool,
) (OrderId, error) {
	market, err := markets.GetByAssetsAndExchange(baseAssetId, quoteAssetId, exchangeId)
	if err != nil {
		return 0, err
	}
	args, err := json.Marshal(OrderParams{
		BotToken:   config.BotToken,
		Leverage:   config.DefaultLeverage,
		ExchangeId: exchangeId,
		MarketId:   market.Id,
		Volume:     amount,
		Price:      &price,
		IsSell:     isSell,
	})
	if err != nil {
		return 0, err
	}
	responseBody, err := call("trader.place_order", string(args))
	if err != nil {
		return 0, err
	}
	responseBodyString, _ := responseBody.(string)
	response := OrderResponse{}
	err = json.Unmarshal([]byte(responseBodyString), &response)
	if err != nil {
		return 0, err
	}
	if response.Code != 0 {
		return 0, fmt.Errorf("OrderPlaceMentFailed:code:%d", response.Code)
	}
	return OrderId(response.Id), nil
}
