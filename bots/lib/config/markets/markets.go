package markets

import (
	"bots/lib/config/exchanges"
	"bots/lib/config/pairs"
)

func Load() {}

type Market struct {
	id       int64
	pair     pairs.Pair
	exchange exchanges.Exchange
}

var (
	NobitexUsdtRls Market = Market{1, pairs.UsdtRls, exchanges.Nobitex}
)
