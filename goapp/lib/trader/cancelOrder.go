package trader

import (
	"encoding/json"
	"fmt"
	"goapp/lib/config"
)

type CancelOrderParams struct {
	BotToken string  `json:"bot_token"`
	Id       OrderId `json:"order_id"`
}

func CancelOrder(id OrderId) error {
	args, err := json.Marshal(CancelOrderParams{
		BotToken: config.BotToken,
		Id:       id,
	})
	if err != nil {
		return err
	}
	responseBody, err := call("trader.cancel_order", string(args))
	if err != nil {
		return err
	}
	responseBodyString, _ := responseBody.(string)
	response := OrderResponse{}
	err = json.Unmarshal([]byte(responseBodyString), &response)
	if err != nil {
		return err
	}
	if response.Code != 0 {
		return fmt.Errorf("OrderPlaceMentFailed:code:%d", response.Code)
	}
	return nil
}
