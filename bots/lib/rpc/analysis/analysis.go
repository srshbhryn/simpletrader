package analysis

import (
	"github.com/gomodule/redigo/redis"
	"github.com/srshbhryn/gocelery"
)

func Load(redisPool *redis.Pool) {
	backend = gocelery.NewRedisRPCcBackend(redisPool)
	// initialize celery client
	var err error
	broker := gocelery.NewRedisBroker(redisPool)
	broker.QueueName = "analysis_query"
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
