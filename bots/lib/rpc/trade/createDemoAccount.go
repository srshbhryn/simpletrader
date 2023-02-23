package trade

import (
	"bots/lib/config/exchanges"
	"fmt"
)

func GetDemoAccount(exchange exchanges.Exchange) (string, error) {
	r, err := client.Delay(
		"trade.create_demo_account",
		int64(exchange),
	)
	if err != nil {
		return "", err
	}
	response, err := backend.GetResult(r.TaskID)
	if err != nil {
		return "", err
	}
	if response.Status != "SUCCESS" {
		return "", fmt.Errorf(response.Traceback.(string))
	}
	return response.Result.(string), nil
}
