package trader

import (
	"encoding/json"
	"fmt"
	"goapp/lib/config"
	"goapp/lib/config/orderstates"
)

type OrderStatusRequest struct {
	BotToken string  `json:"bot_token"`
	Id       OrderId `json:"order_id"`
}

type OrderStatusResponse struct {
	Code     int `json:"code"`
	StatusId int `json:"status_id"`
}

func GetOrderStatus(id OrderId) (*orderstates.OrderState, error) {
	args, err := json.Marshal(OrderStatusRequest{
		BotToken: config.BotToken,
		Id:       id,
	})
	if err != nil {
		return nil, err
	}
	responseBody, err := call("trader.get_order_status", string(args))
	if err != nil {
		return nil, err
	}
	responseBodyString, _ := responseBody.(string)
	response := OrderStatusResponse{}
	err = json.Unmarshal([]byte(responseBodyString), &response)
	if err != nil {
		return nil, err
	}
	if response.Code != 0 {
		return nil, fmt.Errorf("OrderStatusFailed:code:%d", response.Code)
	}
	return orderstates.ById(response.StatusId), nil
}
