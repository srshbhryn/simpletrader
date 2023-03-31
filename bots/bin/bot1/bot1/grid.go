package bot1

import (
	"time"
)

func GenProps() []*Properties {
	props := make([]*Properties, 0)
	for _, LossFunction := range []func(int) float64{SimpleLF, ConstantsLF, ExpoLF, ExpoLF2} {
		for _, TimeDelta := range []time.Duration{10 * time.Minute, 30 * time.Minute, time.Hour, 3 * time.Hour} {
			for _, Len := range []int{1, 2, 3, 6} {
				for _, TradeSize := range []float64{10, 25, 40, 100} {
					for _, PriceRoundingPrecision := range []float64{100, 250, 500, 1000, 2000} {
						for _, GainRatio := range []float64{1.002, 1.0025, 1.004, 1.01} {
							for _, MinBaseBalance := range []float64{200, 400, 600, 800} {
								for _, MinQuoteBalance := range []float64{0} {
									for _, CheckInterval := range []time.Duration{15 * time.Second} {
										for _, SideSleepAfterOrderPlacement := range []time.Duration{time.Minute} {
											props = append(props, &Properties{
												LossFunction:                 LossFunction,
												TimeDelta:                    TimeDelta,
												Len:                          Len,
												TradeSize:                    TradeSize,
												PriceRoundingPrecision:       PriceRoundingPrecision,
												GainRatio:                    GainRatio,
												MinBaseBalance:               MinBaseBalance,
												MinQuoteBalance:              MinQuoteBalance,
												CheckInterval:                CheckInterval,
												SideSleepAfterOrderPlacement: SideSleepAfterOrderPlacement,
											})
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
	return props
}
