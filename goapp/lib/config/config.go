package config

import (
	"goapp/config/assets"
)

func Load() {}

func init() {
	assets.Load()
	// exchanges.Load()
	// orderstates.Load()
	// markets.Load()
}
