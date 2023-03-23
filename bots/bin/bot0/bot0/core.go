package bot0

import (
	"bots/lib/bookwatch"
	"bots/lib/rpc/analysis"
	"time"
)

func (b *SimpleBot) getCenterPrice() (float64, error) {
	roundedPrices, err := analysis.GetRoundedPriceVolume(
		b.Market,
		time.Now().Add(time.Duration(-b.Len-2)*b.TimeDelta),
		time.Now().Add(b.TimeDelta),
		b.TimeDelta,
		b.PriceRoundingPrecision,
	)
	if err != nil {
		return 0, err
	}
	pricesTotalVolume := make(map[float64]float64)
	add := func(price float64, volume float64) {
		vol, ok := pricesTotalVolume[price]
		if !ok {
			pricesTotalVolume[price] = volume
		} else {
			pricesTotalVolume[price] = vol + volume
		}

	}
	factor := 1.0
	for i := 1; i <= b.Len+1; i++ {
		for _, p := range roundedPrices.Prices {
			add(p, roundedPrices.Volumes[roundedPrices.TimeBuckets[len(roundedPrices.TimeBuckets)-i]][p])
		}
		factor *= .8
	}
	totalVol := 0.0
	totalVolPrice := 0.0
	for price, vol := range pricesTotalVolume {
		totalVol += vol
		totalVolPrice += vol * price
	}
	return totalVolPrice / totalVol, nil
}

func (b *SimpleBot) buyer() {
	for {
		time.Sleep(b.CheckInterval)
		if b.quoteBalance < b.MinQuoteBalance {
			continue
		}

		centerPrice, err := b.getCenterPrice()
		if err != nil {
			b.ErrorHandler(err)
			continue
		}
		book, err := bookwatch.ReadBook(b.Market)
		if err != nil {
			b.ErrorHandler(err)
			continue
		}
		desirablePrice := centerPrice / b.GainRatio
		if book.BestBidPrice > desirablePrice {
			continue
		}
		order := pool.Get().(*Order)
		order.amount = b.TradeSize
		order.price = book.BestBidPrice
		order.isSell = false
		b.orderChannel <- order
		time.Sleep(b.SideSleepAfterOrderPlacement)
	}
}

func (b *SimpleBot) seller() {
	for {
		time.Sleep(b.CheckInterval)
		if b.baseBalance < b.MinBaseBalance {
			continue
		}

		centerPrice, err := b.getCenterPrice()
		if err != nil {
			b.ErrorHandler(err)
			continue
		}
		book, err := bookwatch.ReadBook(b.Market)
		if err != nil {
			b.ErrorHandler(err)
			continue
		}
		desirablePrice := centerPrice * b.GainRatio
		if book.BestAskPrice < desirablePrice {
			continue
		}
		order := pool.Get().(*Order)
		order.amount = b.TradeSize
		order.price = book.BestAskPrice
		order.isSell = true
		b.orderChannel <- order
		time.Sleep(b.SideSleepAfterOrderPlacement)
	}
}
