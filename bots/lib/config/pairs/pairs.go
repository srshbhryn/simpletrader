package pairs

import "bots/lib/config/assets"

func Load() {}

type Pair struct {
	Id         int64
	BaseAsset  assets.Asset
	QuoteAsset assets.Asset
}

var (
	UsdtRls  Pair = Pair{1, assets.USDT, assets.RLS}
	BtcUsdt       = Pair{1000, assets.BTC, assets.USDT}
	BtcRls        = Pair{1001, assets.BTC, assets.RLS}
	WbtcUsdt      = Pair{1010, assets.WBTC, assets.USDT}
	WbtcRls       = Pair{1011, assets.WBTC, assets.RLS}
	EthUsdt       = Pair{1020, assets.ETH, assets.USDT}
	EthRls        = Pair{1021, assets.ETH, assets.RLS}
	DogeUsdt      = Pair{1030, assets.DOGE, assets.USDT}
	DogeRls       = Pair{1031, assets.DOGE, assets.RLS}
	ShibUsdt      = Pair{1040, assets.SHIB, assets.USDT}
	ShibRls       = Pair{1041, assets.SHIB, assets.RLS}
)
