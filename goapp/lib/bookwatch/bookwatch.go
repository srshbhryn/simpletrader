package bookwatch

import (
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

// func ExampleClient() {
// 	rdb := Client()
// 	err := rdb.Set(ctx, "key", "value", 0).Err()
// 	if err != nil {
// 		panic(err)
// 	}

// 	val, err := rdb.Get(ctx, "key").Result()
// 	if err != nil {
// 		panic(err)
// 	}
// 	fmt.Println("key", val)

// 	val2, err := rdb.Get(ctx, "key2").Result()
// 	if err == redis.Nil {
// 		fmt.Println("key2 does not exist")
// 	} else if err != nil {
// 		panic(err)
// 	} else {
// 		fmt.Println("key2", val2)
// 	}
// 	// Output: key value
// 	// key2 does not exist
// 	fmt.Println("=============================")
// 	val, err = rdb.Get(ctx, "97").Result()
// 	if err == redis.Nil {
// 		fmt.Println("!!!!!!!!!!!")
// 		fmt.Println("key does not exist")
// 	} else if err != nil {
// 		fmt.Println("!!!!!!!!!!!")
// 		panic(err)
// 	} else {
// 		fmt.Println("val:")
// 		fmt.Println(val)
// 	}
// 	// records, err := csvReader.ReadAll()
// 	// if err != nil {
// 	// 	log.Fatal("Unable to parse file as CSV for "+filePath, err)
// 	// }

// }

func ReadBook(marketId int) (*Book, error) {
	msg, err := rdb.Get(ctx, strconv.Itoa(marketId)).Result()
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
