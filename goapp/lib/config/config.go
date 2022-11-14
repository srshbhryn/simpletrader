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

var BotToken = loadBotToken()

var DefaultLeverage = loadDefaultLeverage()
