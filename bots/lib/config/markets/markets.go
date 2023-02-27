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
	NobitexUsdtRls  Market = Market{1, pairs.UsdtRls, exchanges.Nobitex}
	NobitexBtcUsdt         = Market{2, pairs.BtcUsdt, exchanges.Nobitex}
	NobitexBtcRls          = Market{3, pairs.BtcRls, exchanges.Nobitex}
	NobitexWbtcUsdt        = Market{4, pairs.WbtcUsdt, exchanges.Nobitex}
	NobitexWbtcRls         = Market{5, pairs.WbtcRls, exchanges.Nobitex}
	NobitexEthUsdt         = Market{6, pairs.EthUsdt, exchanges.Nobitex}
	NobitexEthRls          = Market{7, pairs.EthRls, exchanges.Nobitex}
	NobitexDogeUsdt        = Market{8, pairs.DogeUsdt, exchanges.Nobitex}
	NobitexDogeRls         = Market{9, pairs.DogeRls, exchanges.Nobitex}
	NobitexShibUsdt        = Market{10, pairs.ShibUsdt, exchanges.Nobitex}
	NobitexShibRls         = Market{11, pairs.ShibRls, exchanges.Nobitex}
)
