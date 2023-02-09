package main

import (
	"bots/lib/rpc"
	"bots/lib/rpc/analysis"
	"fmt"
	"time"
)

func main() {
	// res, err := rpc.CeleryClient.Delay("analysis.q.get_prices_volume", "1", fmt.Sprintf("%f", fromTimestamp), fmt.Sprintf("%f", toTimestamp), buketSize, "100")
	rpc.Load()
	res, err := analysis.GetRoundedPriceVolume(
		1,
		time.Now().Add(time.Duration(-10*time.Minute)),
		time.Now(),
		time.Minute,
		250.0,
	)
	if err != nil {
		panic(err)
	}
	fmt.Println(res)
	fmt.Printf("                ")
	for _, tb := range res.TimeBuckets {
		fmt.Printf("%d\t", tb.Unix())
	}
	fmt.Printf("\n")
	for _, p := range res.Prices {
		fmt.Printf("%f\t", p)
		for _, tb := range res.TimeBuckets {
			fmt.Printf("%f\t", res.Volumes[tb][p])
		}
		fmt.Printf("\n")
	}

	// response, err := rpc.GetResult(res.TaskID)
	// fmt.Println(response)
	// 	{'market_id': 1,
	// 	'from_datetime': 1675960251.92307,
	// 	'to_datetime': 1675963851.923083,
	// 	'bucket_size': 60.0,
	// 	'price_rounding_precision': Decimal('100')
	// }

}
