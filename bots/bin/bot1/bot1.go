package main

import (
	"bots/bin/bot1/bot1"
	"bots/lib/rpc"
	"bots/lib/utils"
	"fmt"
	"time"
)

func genWorker(ch chan *bot1.Properties) {
	for p := range ch {
		b, err := bot1.New(p)
		if err != nil {
			fmt.Println(err)
		} else {
			b.Run()
		}
	}
}

func main() {
	utils.InitSentry()
	rpc.Load()
	props := bot1.GenProps()
	ch := make(chan *bot1.Properties)
	for i := 0; i < 64; i++ {
		go genWorker(ch)
	}
	for _, p := range props {
		ch <- p
	}
	for {
		time.Sleep(time.Hour)
		close(ch)
	}
}
