package arbitrage

import (
	"goapp/lib/config/assets"
	"goapp/lib/config/exchanges"
	"goapp/lib/config/markets"
)

type order struct {
	isSell bool
	price  float64
	amount float64
	market markets.Market
}

type FixedGRTrader struct {
	baseAsset         assets.Asset
	quoteAsset        assets.Asset
	primaryExchange   exchanges.Exchange
	secondaryExchange exchanges.Exchange
	orders            []order
	feeFactor         float64
}

func New(
	baseAssetId int,
	quoteAssetId int,
	primaryExchangeId int,
	secondaryExchangeId int,
) (*FixedGRTrader, error) {
	for _, exchangeId := range []int{primaryExchangeId, secondaryExchangeId} {
		if _, err := markets.GetByAssetsAndExchange(baseAssetId, quoteAssetId, exchangeId); err != nil {
			return nil, err
		}
	}
	primaryExchange := *exchanges.ById(primaryExchangeId)
	secondaryExchange := *exchanges.ById(secondaryExchangeId)
	feeFactor := (1 - primaryExchange.MakerFee) * (1 - secondaryExchange.TakerFee)
	return &FixedGRTrader{
		baseAsset:         *assets.ById(baseAssetId),
		quoteAsset:        *assets.ById(quoteAssetId),
		primaryExchange:   primaryExchange,
		secondaryExchange: secondaryExchange,
		feeFactor:         feeFactor,
	}, nil
}

func (t *FixedGRTrader) Run() {

}

func (t *FixedGRTrader) primaryMarketBestPrice(isSell bool) float64 {

	return 0
}
