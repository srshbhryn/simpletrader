package main

import (
	"bots/lib/config"
	"bots/lib/config/assets"
	"bots/lib/rpc"
	"bots/lib/rpc/analysis"
	"bots/lib/rpc/trade"
	"fmt"
	"sync"
	"time"
)

func main() {
	getAsset()
}

func getAsset() {
	rpc.Load()
	config.Load()
	var wg sync.WaitGroup
	var c int = 0
	wg.Add(200)

	for i := 0; i < 100; i++ {
		go func() {
			fmt.Println(analysis.GetRoundedPriceVolume(1, time.Now().Add(-time.Hour), time.Now(), time.Duration(10*time.Second), 100))
			c++
			wg.Done()
		}()

		go func() {
			fmt.Println(trade.GetBalance(assets.ETC))
			c++
			wg.Done()

		}()
	}
	wg.Wait()

}
