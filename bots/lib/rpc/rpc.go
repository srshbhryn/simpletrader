package rpc

import (
	"os"

	"github.com/gomodule/redigo/redis"
	"github.com/srshbhryn/gocelery"
)

func Load() {}

var CeleryClient *gocelery.CeleryClient
var backend gocelery.CeleryBackend

func GetResult(taskID string) (*gocelery.ResultMessage, error) {
	return backend.GetResult(taskID)
}

func init() {
	redisPool := &redis.Pool{
		Dial: func() (redis.Conn, error) {
			c, err := redis.DialURL(os.Getenv("RPC_REDIS"))
			if err != nil {
				return nil, err
			}
			return c, err
		},
	}
	backend = gocelery.NewRedisRPCcBackend(redisPool)
	// initialize celery client
	var err error
	broker := gocelery.NewRedisBroker(redisPool)
	broker.QueueName = "analysis_query"
	CeleryClient, err = gocelery.NewCeleryClient(
		broker,
		backend,
		32,
	)
	if err != nil {
		panic(err)
	}

	// broker := gocelery.NewRedisBroker(redisPool)
	// broker.QueueName = "analysis_query"
	// backend := gocelery.NewRedisRPCcBackend(redisPool)
	// client, _ = gocelery.NewCeleryClient(
	// 	broker,
	// 	backend,
	// 	32,
	// )

}
