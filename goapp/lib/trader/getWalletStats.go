package trader

import (
	"encoding/json"
	"fmt"
	"goapp/lib/config"
	"time"
)

type WalletsStatsRequest struct {
	BotToken   string `json:"bot_token"`
	ExchangeId int    `json:"exchange_id"`
	AssetId    int    `json:"asset_id"`
}

type WalletsStats struct {
	Code           int       `json:"code"`
	Timestamp      time.Time `json:"timestamp"`
	FreeBalance    float64   `json:"free_balance"`
	BlockedBalance float64   `json:"blocked_balance"`
}

func GetWalletsStats(assetId int, exchangeId int) (*WalletsStats, error) {
	args, err := json.Marshal(WalletsStatsRequest{
		BotToken:   config.BotToken,
		AssetId:    assetId,
		ExchangeId: exchangeId,
	})
	if err != nil {
		return nil, err
	}
	responseBody, err := call("trader.get_balance", string(args))
	if err != nil {
		return nil, err
	}
	responseBodyString, _ := responseBody.(string)
	walletsStats := WalletsStats{}
	err = json.Unmarshal([]byte(responseBodyString), &walletsStats)
	if err != nil {
		return nil, err
	}
	if walletsStats.Code != 0 {
		return nil, fmt.Errorf("WalletsStats:code:%d", walletsStats.Code)
	}
	return &walletsStats, nil
}
