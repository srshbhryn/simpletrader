package rpc

import (
	"os"

	"github.com/gomodule/redigo/redis"
)

var redisPool *redis.Pool

func init() {
	redisPool = &redis.Pool{
		Dial: func() (redis.Conn, error) {
			c, err := redis.DialURL(os.Getenv("RPC_REDIS"))
			if err != nil {
				return nil, err
			}
			return c, err
		},
	}
}
