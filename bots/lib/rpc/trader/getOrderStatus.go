package trader

import (
	"bots/lib/config/orderstates"
	"fmt"
	"strconv"

	uuid "github.com/satori/go.uuid"
)

type OrderState struct {
	State        orderstates.OrderState
	FilledAmount float64
}

func (t *Trader) GetOrderStatus(OrderUUID uuid.UUID) (*OrderState, error) {
	r, err := client.Delay("trade.get_order_status", fmt.Sprintf("%s", OrderUUID))
	if err != nil {
		return nil, err
	}
	response, err := backend.GetResult(r.TaskID)
	if err != nil {
		return nil, err
	}
	if response.Status != "SUCCESS" {
		return nil, fmt.Errorf(response.Traceback.(string))
	}
	result := response.Result
	filledAmount, err := strconv.ParseFloat(result.(map[string]interface{})["filled_volume"].(string), 64)
	state := orderstates.OrderState(result.(map[string]interface{})["status_id"].(float64))
	return &OrderState{
		state,
		filledAmount,
	}, nil
}
