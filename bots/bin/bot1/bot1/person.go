package bot1

import (
	"bots/lib/config/exchanges"
	"bots/lib/config/markets"
	"bots/lib/rpc/trade"
	"bots/lib/rpc/trader"
	"fmt"
	"log"
	"time"

	"github.com/getsentry/sentry-go"
	uuid "github.com/satori/go.uuid"
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
	trader       *trader.Trader
	baseBalance  float64
	quoteBalance float64
	orderIds     []*uuid.UUID
	orderChannel chan *Order
}

type Bot struct {
	Constants
	Properties
	Attributes
}

func (b *Bot) log() {
	log.Println(b)
}

func New(p *Properties) (*Bot, error) {
	cons := Constants{
		markets.NobitexUsdtRls,
		func(err error) { sentry.CaptureException(err) },
	}
	start := time.Now()
	accountId, err := trade.GetDemoAccount(exchanges.Nobitex)
	total := time.Now().Sub(start)
	fmt.Println(total)
	if err != nil {
		return nil, err
	}
	trader, _ := trader.Create(exchanges.Nobitex, accountId)
	att := Attributes{
		accountId:    accountId,
		trader:       trader,
		baseBalance:  0,
		quoteBalance: 0,
		orderIds:     make([]*uuid.UUID, 0),
		orderChannel: make(chan *Order, 16),
	}
	return &Bot{cons, *p, att}, nil
}

func (b *Bot) Run() {
	go b.buyer()
	go b.seller()
	go b.placeOrders()
	go b.updateBalances()
}
