package bookwatch

import (
	"bots/lib/config/markets"
	"context"
	"encoding/csv"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/go-redis/redis/v8"
)

type Book struct {
	Timestamp     time.Time
	BestAskPrice  float64
	BestAskVolume float64
	BestBidPrice  float64
	BestBidVolume float64
}

var rdb *redis.Client
var ctx = context.Background()

func Load() {}
func init() {
	db, err := strconv.Atoi(os.Getenv("BOOKWATCH_REDIS_DB"))
	if err != nil {
		panic(err)
	}
	rdb = redis.NewClient(&redis.Options{
		Addr:     os.Getenv("BOOKWATCH_REDIS_HOST"),
		Password: "",
		DB:       db,
	})
}

func ReadBook(market markets.Market) (*Book, error) {
	msg, err := rdb.Get(ctx, strconv.Itoa(int(market.Id))).Result()
	if err != nil {
		return nil, err
	}
	rd := csv.NewReader(strings.NewReader(msg))
	val, err := rd.Read()
	if err != nil {
		return nil, err
	}
	timeStamp, err := strconv.ParseInt(val[0], 10, 64)
	if err != nil {
		return nil, err
	}
	seconds := timeStamp / 1000
	nanoseconds := (timeStamp - seconds*1000) * 1000000
	bestAskPrice, err := strconv.ParseFloat(val[1], 64)
	if err != nil {
		return nil, err
	}
	bestAskVolume, err := strconv.ParseFloat(val[2], 64)
	if err != nil {
		return nil, err
	}
	BestBidPrice, err := strconv.ParseFloat(val[3], 64)
	if err != nil {
		return nil, err
	}
	bestBidVolume, err := strconv.ParseFloat(val[4], 64)
	if err != nil {
		return nil, err
	}

	return &Book{
		Timestamp:     time.Unix(seconds, nanoseconds),
		BestAskPrice:  bestAskPrice,
		BestAskVolume: bestAskVolume,
		BestBidPrice:  BestBidPrice,
		BestBidVolume: bestBidVolume,
	}, nil
}
