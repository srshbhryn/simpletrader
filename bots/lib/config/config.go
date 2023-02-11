package config

import (
	"bots/lib/config/assets"
	"bots/lib/config/exchanges"
	"bots/lib/config/markets"
	"bots/lib/config/orderstates"
	"bots/lib/config/pairs"
	"os"
)

func Load() {}

func init() {
	assets.Load()
	pairs.Load()
	exchanges.Load()
	orderstates.Load()
	markets.Load()
	loadAccountUUID()
}

var AccountUUID string

func loadAccountUUID() {
	AccountUUID = os.Getenv("ACCOUNT_UUID")
}
