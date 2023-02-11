package trade

import (
	"bots/lib/config/orderstates"
	"fmt"

	uuid "github.com/satori/go.uuid"
)

type OrderState struct {
	State        orderstates.OrderState
	FilledAmount float64
}

func GetOrderStatus(OrderUUID uuid.UUID) (*OrderState, error) {
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
	return &OrderState{
		result.(map[string]orderstates.OrderState)["status_id"],
		result.(map[string]float64)["filled_amount"],
	}, nil
}
