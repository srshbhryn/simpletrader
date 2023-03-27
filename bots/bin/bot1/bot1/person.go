package bot1

import (
	"bots/lib/config/markets"
	"time"

	"github.com/google/uuid"
)

type Constants struct {
	Market       markets.Market
	ErrorHandler func(error)
}
type Properties struct {
	LossFunction                 func(n int) float64
	TimeDelta                    time.Duration
	Len                          int
	TradeSize                    float64
	PriceRoundingPrecision       float64
	GainRatio                    float64
	MinBaseBalance               float64
	MinQuoteBalance              float64
	CheckInterval                time.Duration
	SideSleepAfterOrderPlacement time.Duration
}

type Attributes struct {
	accountId    string
	baseBalance  float64
	quoteBalance float64
	orderIds     []*uuid.UUID
	orderChannel chan *Order
}
