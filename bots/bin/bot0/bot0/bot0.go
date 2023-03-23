package bot0

import (
	"bots/lib/config/markets"
	"time"

	uuid "github.com/satori/go.uuid"
)

type SimpleBotConfig struct {
	Market                       markets.Market
	TimeDelta                    time.Duration
	Len                          int
	PriceRoundingPrecision       float64
	TradeSize                    float64
	StopLossRatio                float64
	GainRatio                    float64
	MinBaseBalance               float64
	MinQuoteBalance              float64
	ErrorHandler                 func(error)
	CheckInterval                time.Duration
	SideSleepAfterOrderPlacement time.Duration
}

type SimpleBot struct {
	SimpleBotConfig
	accountId    string
	baseBalance  float64
	quoteBalance float64
	orderIds     []*uuid.UUID
	orderChannel chan *Order
}

func New(conf *SimpleBotConfig) *SimpleBot {
	bot := &SimpleBot{
		SimpleBotConfig: *conf,
		accountId:       "",
		baseBalance:     0,
		quoteBalance:    0,
		orderIds:        make([]*uuid.UUID, 0),
		orderChannel:    make(chan *Order, 16),
	}
	return bot
}

func (b *SimpleBot) Run() {
	go b.buyer()
	go b.seller()
	go b.placeOrders()
	go b.updateBalances()
}
