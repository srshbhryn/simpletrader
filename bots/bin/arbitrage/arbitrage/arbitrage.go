package arbitrage

import (
	"fmt"
	"bots/lib/bookwatch"
	"bots/lib/config"
	"bots/lib/config/assets"
	"bots/lib/config/exchanges"
	"bots/lib/config/markets"
	"sync"
)

type MarketPair struct {
	NobitexMarket *markets.Market
	KucoinMarket  *markets.Market
}

type Opportunity struct {
	Amount    float64
	GainRatio float64
}

func GetKucoinArbitrageMarkets() []*MarketPair {
	usdtId := assets.ByName("usdt").Id
	kucoinId := exchanges.ByName("kucoin_futures").Id
	nobitexId := exchanges.ByName("nobitex").Id
	marketPairs := make([]*MarketPair, 0)
	for _, asset := range *assets.All() {
		nobitexMarket, err := markets.GetByAssetsAndExchange(asset.Id, usdtId, nobitexId)
		if err != nil {
			continue
		}
		kucoinMarket, err := markets.GetByAssetsAndExchange(asset.Id, usdtId, kucoinId)
		if err != nil {
			continue
		}
		marketPairs = append(marketPairs, &MarketPair{
			NobitexMarket: nobitexMarket,
			KucoinMarket:  kucoinMarket,
		})
	}
	return marketPairs
}

func (pair *MarketPair) GetAmount(isSell bool) (*Opportunity, error) {
	if isSell {
		op, err := pair.getSellAmount()
		if err != nil {
			return nil, err
		}
		return op, nil
	}
	op, err := pair.getBuyAmount()
	if err != nil {
		return nil, err
	}
	return op, nil
}

func getFeeFactor() float64 {
	return (1 - config.NobitexFee) * (1 - config.KucoinFuturesFee)
}

var feeFactor = getFeeFactor()

var safetyFactor = 1.002

func (pair *MarketPair) getMinSellPrice() (float64, error) {
	book, err := bookwatch.ReadBook(pair.KucoinMarket.Id)
	if err != nil {
		return 0, err
	}
	return (book.BestAskPrice / feeFactor) * safetyFactor, nil
}

func (pair *MarketPair) getMaxBuyPrice() (float64, error) {
}

// TODO: NOT TOO MUCH DATA ?????
func (pair *MarketPair) getSellAmount() (*Opportunity, error) {
	var gotError sync.Mutex
	var returningError error
	var wg sync.WaitGroup
	wg.Add(2)
	// TODO check Balance
	var minSellPrice float64
	var nobitexSellPrice float64
	var nobitexSellVolume float64
	go func() {
		defer wg.Done()
		var err error
		minSellPrice, err = pair.getMinSellPrice()
		if err != nil {
			if gotError.TryLock() {
				returningError = err
			}
		}
	}()
	go func() {
		defer wg.Done()
		book, err := bookwatch.ReadBook(pair.NobitexMarket.Id)
		if err != nil {
			if gotError.TryLock() {
				returningError = err
			}
			return
		}
		nobitexSellPrice = book.BestBidPrice
		nobitexSellVolume = book.BestBidVolume
	}()
	wg.Wait()
	if !gotError.TryLock() {
		return 0, returningError
	}
	if nobitexSellPrice < minSellPrice {
		return 0, fmt.Errorf("BadPrice")
	}
	return nobitexSellVolume, nil
}

func (pair *MarketPair) getBuyAmount() (*Opportunity, error) {
	var gotError sync.Mutex
	var returningError error
	var wg sync.WaitGroup
	wg.Add(2)
	// TODO check Balance
	var maxBuyPrice float64
	var nobitexBuyPrice float64
	var nobitexBuyVolume float64
	setError := func (err error){
		if gotError.TryLock() {
			returningError = err
		}
	}
	go func() {
		defer wg.Done()
		book, err := bookwatch.ReadBook(pair.KucoinMarket.Id)
		if err != nil {
			return 0, err
		}
		return (book.Bes * feeFactor) / safetyFactor, nil
		maxBuyPrice, err = pair.getMaxBuyPrice()
		if err != nil {
			setError(err)
		}
	}()
	go func() {
		defer wg.Done()
		book, err := bookwatch.ReadBook(pair.NobitexMarket.Id)
		if err != nil {
			setError(err)
			return
		}
		nobitexBuyPrice = book.BestAskPrice
		nobitexBuyVolume = book.BestAskVolume
	}()
	wg.Wait()
	if !gotError.TryLock() {
		return 0, returningError
	}
	if nobitexBuyPrice > maxBuyPrice {
		return 0, fmt.Errorf("BadPrice")
	}
	return &Opportunity{Amount: nobitexBuyVolume, GainRatio: }, nil
}
