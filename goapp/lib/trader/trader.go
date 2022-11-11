package trader

import (
	"errors"
	"fmt"
	"os"
	"time"

	"github.com/gomodule/redigo/redis"
	"github.com/srshbhryn/gocelery"
)

func Load() {}

var client *gocelery.CeleryClient

func init() {
	redisPool := &redis.Pool{
		Dial: func() (redis.Conn, error) {
			c, err := redis.DialURL(os.Getenv("REDIS"))
			if err != nil {
				return nil, err
			}
			return c, err
		},
	}
	broker := gocelery.NewRedisBroker(redisPool)
	broker.QueueName = "trader"
	client, _ = gocelery.NewCeleryClient(
		broker,
		&gocelery.RedisCeleryBackend{Pool: redisPool},
		100,
	)

}

func Call(taskName string, args string) (interface{}, error) {
	asyncResult, err := client.Delay(taskName, args)
	if err != nil {
		return nil, err
	}
	res, err := GetResult(asyncResult, 10*time.Second)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func GetResult(ar *gocelery.AsyncResult, timeout time.Duration) (interface{}, error) {
	ticker := time.NewTicker(100 * time.Microsecond)
	timeoutChan := time.After(timeout)
	for {
		select {
		case <-timeoutChan:
			err := fmt.Errorf("%v timeout getting result for %s", timeout, ar.TaskID)
			return nil, err
		case <-ticker.C:
			val, err := ar.AsyncGet()
			if errors.Is(err, gocelery.TaskFailedError) {
				return nil, err
			}
			if err != nil {
				continue
			}
			return val, nil
		}
	}
}
