package config

import (
	"goapp/lib/config/assets"
)

func Load() {}

func init() {
	assets.Load()
	// exchanges.Load()
	// orderstates.Load()
	// markets.Load()
}
