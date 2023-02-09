package main

import (
	"bots/lib/rpc"
	"fmt"
	"time"
)

func main() {
	toTimestamp := float64(time.Now().UnixMilli()) / 1000
	fromTimestamp := toTimestamp - 100000000
	buketSize := "250.0"

	res, err := rpc.CeleryClient.Delay("analysis.q.get_prices_volume", "1", fmt.Sprintf("%f", fromTimestamp), fmt.Sprintf("%f", toTimestamp), buketSize, "100")
	fmt.Println("analysis.q.get_prices_volume", "1", fmt.Sprintf("%f", fromTimestamp), fmt.Sprintf("%f", toTimestamp), buketSize, "100")
	if err != nil {
		panic(err)
	}
	response, err := rpc.GetResult(res.TaskID)
	fmt.Println(response)
	// 	{'market_id': 1,
	// 	'from_datetime': 1675960251.92307,
	// 	'to_datetime': 1675963851.923083,
	// 	'bucket_size': 60.0,
	// 	'price_rounding_precision': Decimal('100')
	// }

}
