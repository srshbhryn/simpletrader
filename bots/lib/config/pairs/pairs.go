package pairs

import "bots/lib/config/assets"

func Load() {}

type Pair struct {
	Id         int64
	BaseAsset  assets.Asset
	QuoteAsset assets.Asset
}

var (
	UsdtRls Pair = Pair{1, assets.USDT, assets.RLS}
)
