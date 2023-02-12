package main

import (
	"bots/lib/bookwatch"
	"bots/lib/config"
	"bots/lib/config/markets"
	"bots/lib/rpc"
	"fmt"
	"time"
)

func main() {
	getAsset()
}

func getAsset() {
	rpc.Load()
	config.Load()
	bookwatch.Load()
	var totalTime int64 = 0
	for i := 0; i < 1000; i++ {
		time.Sleep(time.Millisecond * 10)
		start := time.Now().UnixMicro()
		book, err := bookwatch.ReadBook(markets.NobitexUsdtRls)
		if err != nil {
			panic(err)
		}
		totalTime += time.Now().UnixMicro() - start
		fmt.Println(time.Now().Sub(book.Timestamp))
	}
	fmt.Println(float64(totalTime) / 1000)
	// var wg sync.WaitGroup
	// var c int = 0
	// wg.Add(200)

	// for i := 0; i < 100; i++ {
	// 	go func() {
	// 		fmt.Println(analysis.GetRoundedPriceVolume(1, time.Now().Add(-time.Hour), time.Now(), time.Duration(10*time.Second), 100))
	// 		c++
	// 		wg.Done()
	// 	}()

	// 	go func() {
	// 		fmt.Println(trade.GetBalance(assets.ETC))
	// 		c++
	// 		wg.Done()

	// 	}()
	// }
	// wg.Wait()

}
