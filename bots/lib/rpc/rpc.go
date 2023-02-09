package rpc

import (
	"bots/lib/rpc/analysis"
	"bots/lib/rpc/trader"
)

func Load() {
	analysis.Load(redisPool)
	trader.Load()
}
