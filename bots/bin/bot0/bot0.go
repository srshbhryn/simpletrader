package main

import (
	"bots/lib/config"
	"bots/lib/rpc"
	"fmt"
	"time"

	"github.com/gomodule/redigo/redis"
	"github.com/srshbhryn/gocelery"
)

func main() {
	rpc.Load()
	config.Load()
	redisPool := &redis.Pool{
		Dial: func() (redis.Conn, error) {
			c, err := redis.DialURL("redis://127.0.0.1:6379/3")
			if err != nil {
				return nil, err
			}
			return c, err
		},
		TestOnBorrow: func(c redis.Conn, t time.Time) error {
			_, err := c.Do("PING")
			return err
		},
		MaxIdle:         32,
		MaxActive:       32,
		Wait:            false,
		MaxConnLifetime: time.Duration(10 * time.Hour),
	}
	backend := gocelery.NewRedisRPCcBackend(redisPool)
	broker := gocelery.NewRedisBroker(redisPool)
	broker.QueueName = "trade_rpc"

	// initialize celery client
	cli, _ := gocelery.NewCeleryClient(
		broker,
		backend,
		16,
	)
	// prepare arguments
	taskName := "trade.get_balance"
	argA := "99994715bc10442f85a1de3a8bad9896"
	argB := "13"
	// run task
	for i := 0; i < 10; i++ {
		time.Sleep(time.Second)
		// go func() {
		ar, err := cli.Delay(taskName, argA, argB)
		if err != nil {
			panic(err)
		}
		fmt.Println("X")
		r, err := backend.GetResult(ar.TaskID)
		fmt.Println("Y")
		fmt.Println(r)
	}
	time.Sleep(30 * time.Second)
}
