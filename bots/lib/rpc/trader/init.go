package trader

import (
	"bots/lib/config/exchanges"
	"fmt"

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

func getDemoAccount(exchange exchanges.Exchange) (string, error) {
	r, err := client.Delay(
		"trade.create_demo_account",
		int64(exchange),
	)
	if err != nil {
		return "", err
	}
	response, err := backend.GetResult(r.TaskID)
	if err != nil {
		return "", err
	}
	if response.Status != "SUCCESS" {
		return "", fmt.Errorf(response.Traceback.(string))
	}
	return response.Result.(string), nil
}
