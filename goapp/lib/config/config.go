package config

import (
	"goapp/lib/config/assets"
	"goapp/lib/config/exchanges"
	"goapp/lib/config/markets"
	"goapp/lib/config/orderstates"
	"os"
	"strconv"
)

func Load() {}

func init() {
	assets.Load()
	exchanges.Load()
	orderstates.Load()
	markets.Load()
}

func loadBotToken() string {
	return os.Getenv("TOKEN")
}

func loadDefaultLeverage() *int {
	l, err := strconv.Atoi(os.Getenv("LEVERAGE"))
	if err != nil {
		panic(err)
	}
	return &l
}

func loadNobitexFee() float64 {
	fee, err := strconv.ParseFloat(os.Getenv("NOBITEX_FEE"), 64)
	if err != nil {
		panic(fee)
	}
	return fee
}

func loadKucoinFuturesFee() float64 {
	fee, err := strconv.ParseFloat(os.Getenv("KUCOIN_FUTURES_FEE"), 64)
	if err != nil {
		panic(fee)
	}
	return fee

}

var BotToken = loadBotToken()

var DefaultLeverage = loadDefaultLeverage()

var NobitexFee = loadNobitexFee()

var KucoinFuturesFee = loadKucoinFuturesFee()
