package analysis

import (
	"bots/lib/config/markets"
	"fmt"
	"sort"
	"time"
)

type RoundedPriceVolume struct {
	Prices      []float64
	TimeBuckets []time.Time
	Volumes     map[time.Time]map[float64]float64
}

func GetRoundedPriceVolume(
	market markets.Market,
	fromTimestamp time.Time,
	toTimestamp time.Time,
	bucketSize time.Duration,
	priceRoundingPrecision float64,
) (*RoundedPriceVolume, error) {
	r, err := client.Delay(
		"analysis.q.get_prices_volume",
		fmt.Sprintf("%d", market.Id),
		fmt.Sprintf("%f", float64(fromTimestamp.UnixMicro())/1e6),
		fmt.Sprintf("%f", float64(toTimestamp.UnixMicro())/1e6),
		fmt.Sprintf("%f", bucketSize.Seconds()),
		fmt.Sprintf("%f", priceRoundingPrecision),
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
	result := response.Result
	rpv := RoundedPriceVolume{
		Prices:      nil,
		TimeBuckets: nil,
		Volumes:     make(map[time.Time]map[float64]float64),
	}
	prices := make([]float64, 0)
	timeBuckets := make([]time.Time, 0)

	for _, e := range result.([]interface{}) {
		entry := e.(map[string]interface{})
		bucket := time.Unix(int64(entry["bucket"].(float64)), 0)
		price := entry["rounded_price"].(float64)
		volume := entry["total_volume"].(float64)
		func() {
			for _, listedBucket := range timeBuckets {
				if bucket == listedBucket {
					return
				}
			}
			timeBuckets = append(timeBuckets, bucket)
			rpv.Volumes[bucket] = make(map[float64]float64, 64)
		}()

		func() {
			for _, listedPrice := range prices {
				if price == listedPrice {
					return
				}
			}
			prices = append(prices, price)
			rpv.Volumes[bucket][price] = volume
		}()
	}
	sort.Slice(prices, func(i, j int) bool {
		return prices[i] < prices[j]
	})

	sort.Slice(timeBuckets, func(i, j int) bool {
		return timeBuckets[i].Before(timeBuckets[j])
	})
	for _, tb := range timeBuckets {
		for _, p := range prices {
			if _, ok := rpv.Volumes[tb][p]; !ok {
				rpv.Volumes[tb][p] = 0.0
			}
		}
	}
	rpv.Prices = prices
	rpv.TimeBuckets = timeBuckets
	return &rpv, nil

}

func appendIfMissingPrice(slice []interface{}, i interface{}) []interface{} {
	for _, ele := range slice {
		if ele == i {
			return slice
		}
	}
	return append(slice, i)
}
