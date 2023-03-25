package rpc

import (
	"bots/lib/rpc/analysis"
	"bots/lib/rpc/trade"
	"bots/lib/rpc/trader"

	"github.com/srshbhryn/gocelery"
)

func Load() {
	var backend gocelery.CeleryBackend = gocelery.NewRedisRPCcBackend(redisPool)
	analysis.Load(redisPool, backend)
	trade.Load(redisPool, backend)
	trader.Load(redisPool, backend)
}
