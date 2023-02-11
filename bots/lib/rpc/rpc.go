package rpc

import (
	"bots/lib/rpc/analysis"
	"bots/lib/rpc/trade"

	"github.com/srshbhryn/gocelery"
)

func Load() {
	var backend gocelery.CeleryBackend = gocelery.NewRedisRPCcBackend(redisPool)
	analysis.Load(redisPool, backend)
	trade.Load(redisPool, backend)
}
