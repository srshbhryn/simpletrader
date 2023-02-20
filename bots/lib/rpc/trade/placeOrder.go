package trade

import (
	"bots/lib/config"
	"bots/lib/config/pairs"
	"fmt"

	uuid "github.com/satori/go.uuid"
)

func PlaceOrder(
	Pair pairs.Pair,
	Leverage int32,
	Volume float64,
	IsSell bool,
	Price *float64,
	ClientOrderId *string,
) (*uuid.UUID, error) {
	var isSell string = "false"
	var price interface{}
	var clientOrderId interface{}
	if Price != nil {
		price = *Price
	}
	if ClientOrderId != nil {
		clientOrderId = *ClientOrderId
	}
	if IsSell {
		isSell = "true"
	}
	r, err := client.Delay(
		"trade.place_order",
		config.AccountUUID,
		Pair.Id,
		Leverage,
		Volume,
		isSell,
		price,
		clientOrderId,
	)
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
	orderUUID, err := uuid.FromString(response.Result.(string))
	if err != nil {
		return nil, err
	}
	return &orderUUID, err
}
