package bot0

import (
	"bots/lib/bookwatch"
	"bots/lib/config/assets"
	"bots/lib/config/exchanges"
	"bots/lib/config/markets"
	"bots/lib/rpc/analysis"
	"bots/lib/rpc/trade"
	"fmt"
	"math"
	"time"
)

func getFreeBalance(asset assets.Asset) (float64, error) {
	balances, err := trade.GetBalance(asset)
	if err != nil {
		return 0, err
	}
	return balances.Free, nil
}

func initTradeAccount() error {
	accountId, err := trade.GetDemoAccount(exchanges.Nobitex)
	if err != nil {
		return err
	}
	trade.SetAccountUUID(accountId)
	return nil
}

func getBook() {
	bookwatch.ReadBook(markets.NobitexUsdtRls)
}

func Run() error {
	// roundedPrices, err := analysis.GetRoundedPriceVolume(
	// 	markets.NobitexUsdtRls,
	// 	time.Now().Add(-6*time.Hour),
	// 	time.Now(),
	// 	15*time.Minute,
	// 	2000,
	// )
	roundedPrices, err := analysis.GetRoundedPriceVolume(
		markets.NobitexUsdtRls,
		time.Now().Add(-20*time.Hour),
		time.Now(),
		10*time.Minute,
		2000,
	)

	if err != nil {
		return err
	}

	fmt.Printf(roundedPrices.TimeBuckets[0].String()[:20] + "\t")
	for _, p := range roundedPrices.Prices {
		fmt.Printf("%d\t", int64(p))
	}
	fmt.Print("\n")
	fmt.Print("\n")
	for _, ts := range roundedPrices.TimeBuckets {
		fmt.Print(ts.String()[:20] + "\t")
		probs := make([]float64, 0)
		for _, p := range roundedPrices.Prices {
			vol := roundedPrices.Volumes[ts][p]
			prob := vol / roundedPrices.TimeBucketTotalVolume(ts)
			probs = append(probs, prob)
			if prob >= 0.1 {
				fmt.Printf("%.2f\t", prob)
			} else {
				if prob > 0 {
					fmt.Printf("xxxx\t")
				} else {
					fmt.Printf("    \t")
				}
			}
		}
		fmt.Printf("%f\t", roundedPrices.TimeBucketTotalVolume(ts)/1000)
		fmt.Printf("%f\t", entropy(probs))
		fmt.Printf("\n")
	}
	return nil
}

func entropy(probs []float64) float64 {
	var ent float64 = 0
	for _, p := range probs {
		if p == 0 {
			continue
		}
		ent += p * math.Log2(1/p)
	}
	return ent
}
