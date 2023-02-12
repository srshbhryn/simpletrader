package markets

import (
	"bots/lib/config/exchanges"
	"bots/lib/config/pairs"
)

func Load() {}

type Market struct {
	Id       int64
	Pair     pairs.Pair
	Exchange exchanges.Exchange
}

var (
	NobitexUsdtRls Market = Market{1, pairs.UsdtRls, exchanges.Nobitex}
)
