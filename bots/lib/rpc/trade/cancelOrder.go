package trade

import (
	"fmt"

	uuid "github.com/satori/go.uuid"
)

func CancelOrder(orderUUID uuid.UUID) error {
	r, err := client.Delay("trade.cancel_order", fmt.Sprintf("%s", orderUUID))
	if err != nil {
		return err
	}
	response, err := backend.GetResult(r.TaskID)
	if err != nil {
		return err
	}
	if response.Status != "SUCCESS" {
		return fmt.Errorf(response.Traceback.(string))
	}
	return nil
}
