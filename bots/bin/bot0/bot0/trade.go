package bot0

import (
	"bots/lib/rpc/trade"
	"sync"
	"time"
)

type Order struct {
	isSell bool
	amount float64
	price  float64
}

var pool sync.Pool

func init() {
	pool = sync.Pool{
		New: func() interface{} {
			return &Order{}
		},
	}
}

func (b *SimpleBot) placeOrders() {
	for order := range b.orderChannel {
		func(order *Order) {
			defer pool.Put(order)
			clientOrderId := ""
			orderUUID, err := trade.PlaceOrder(b.Market.Pair, 1, order.amount, order.isSell, &order.price, &clientOrderId)
			if err != nil {
				b.ErrorHandler(err)
				return
			}
			b.orderIds = append(b.orderIds, orderUUID)
		}(order)
	}
}

func (b *SimpleBot) updateBalances() {
	for {
		baseBalances, err := trade.GetBalance(b.Market.Pair.BaseAsset)
		if err != nil {
			b.ErrorHandler(err)
		} else {
			b.baseBalance = baseBalances.Free
		}
		quoteBalances, err := trade.GetBalance(b.Market.Pair.QuoteAsset)
		if err != nil {
			b.ErrorHandler(err)
		} else {
			b.quoteBalance = quoteBalances.Free
		}
		time.Sleep(b.CheckInterval)
	}
}
