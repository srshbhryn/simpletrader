package markets

import (
	"encoding/json"
	"goapp/config/assets"
	"goapp/config/exchanges"
	"os"
)

func Load() {}

type MarketJson struct {
	Id           int    `json:"id"`
	BaseAssetId  int    `json:"base_asset_id"`
	QuoteAssetId int    `json:"quote_asset_id"`
	ExchangeId   int    `json:"exchange_id"`
	Symbol       string `json:"symbol"`
}

type Market struct {
	Id         int
	BaseAsset  *assets.Asset
	QuoteAsset *assets.Asset
	Exchange   *exchanges.Exchange
	Symbol     string
}

var instanceById map[int]*Market
var instanceBySymbol map[string]*Market

func GetBySymbol(symbol string) (*Market, error) {
	return instanceBySymbol[symbol], nil
}

func init() {
	configDir := os.Getenv("CONFIG_DIR")
	configFile := configDir + "markets.json"
	load(configFile)
}

func load(filePath string) {
	dat, err := os.ReadFile(filePath)
	if err != nil {
		panic(err)
	}
	var instances []MarketJson
	err = json.Unmarshal(dat, &instances)
	if err != nil {
		panic(err)
	}
	instanceById = make(map[int]*Market)
	instanceBySymbol = make(map[string]*Market)
	for _, instance := range instances {
		market := Market{
			Id:         instance.Id,
			BaseAsset:  assets.ById(instance.BaseAssetId),
			QuoteAsset: assets.ById(instance.QuoteAssetId),
			Symbol:     instance.Symbol,
			Exchange:   exchanges.ById(instance.ExchangeId),
		}
		instanceById[instance.Id] = &market
		instanceBySymbol[instance.Symbol] = &market
	}
}
