package bot1

import (
	"time"
)

func (b *Bot) placeOrders() {
	for order := range b.orderChannel {
		func(order *Order) {
			defer orderPool.Put(order)
			clientOrderId := ""
			orderUUID, err := b.trader.PlaceOrder(b.Market.Pair, 1, order.amount, order.isSell, &order.price, &clientOrderId)
			if err != nil {
				b.ErrorHandler(err)
				return
			}
			b.orderIds = append(b.orderIds, orderUUID)
		}(order)
	}
}

func (b *Bot) updateBalances() {
	for {
		baseBalances, err := b.trader.GetBalance(b.Market.Pair.BaseAsset)
		if err != nil {
			b.ErrorHandler(err)
		} else {
			b.baseBalance = baseBalances.Free
		}
		quoteBalances, err := b.trader.GetBalance(b.Market.Pair.QuoteAsset)
		if err != nil {
			b.ErrorHandler(err)
		} else {
			b.quoteBalance = quoteBalances.Free
		}
		time.Sleep(b.CheckInterval)
	}
}
