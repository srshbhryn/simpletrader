package trade

import (
	"bots/lib/config/assets"
	"fmt"
	"strconv"
)

type Balance struct {
	Free    float64
	Blocked float64
}

func GetBalance(Asset assets.Asset) (*Balance, error) {
	r, err := client.Delay("trade.get_balance", accountUUID, fmt.Sprintf("%d", int64(Asset)))
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
	free, err := strconv.ParseFloat(result.(map[string]interface{})["free"].(string), 64)
	if err != nil {
		return nil, err
	}
	blocked, err := strconv.ParseFloat(result.(map[string]interface{})["blocked"].(string), 64)
	if err != nil {
		return nil, err
	}
	return &Balance{
		Free:    free,
		Blocked: blocked,
	}, nil
}
