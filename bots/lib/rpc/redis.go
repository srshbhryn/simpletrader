package rpc

import (
	"os"
	"time"

	"github.com/gomodule/redigo/redis"
)

var redisPool *redis.Pool

func init() {
	redisPool = &redis.Pool{
		TestOnBorrow: func(c redis.Conn, t time.Time) error {
			_, err := c.Do("PING")
			return err
		},
		MaxIdle:         64,
		MaxActive:       64,
		Wait:            true,
		MaxConnLifetime: time.Duration(10 * time.Hour),
		Dial: func() (redis.Conn, error) {
			c, err := redis.DialURL(os.Getenv("RPC_REDIS"))
			if err != nil {
				return nil, err
			}
			return c, err
		},
	}
}
