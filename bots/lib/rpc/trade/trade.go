package trade

import (
	"github.com/gomodule/redigo/redis"
	"github.com/srshbhryn/gocelery"
)

func Load(redisPool *redis.Pool, celeryBackend gocelery.CeleryBackend) {
	backend = celeryBackend
	var err error
	broker := gocelery.NewRedisBroker(redisPool)
	broker.QueueName = "trade_rpc"
	client, err = gocelery.NewCeleryClient(
		broker,
		backend,
		32,
	)
	if err != nil {
		panic(err)
	}
}

var client *gocelery.CeleryClient
var backend gocelery.CeleryBackend
