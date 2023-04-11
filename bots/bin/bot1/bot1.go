package main

import (
	"bots/bin/bot1/bot1"
	"bots/lib/rpc"
	"bots/lib/utils"
	"fmt"
	"time"

	"github.com/getsentry/sentry-go"
)

func genWorker(ch chan *bot1.Properties) {
	for p := range ch {
		fmt.Println(p)
		b, err := bot1.New(p)
		if err != nil {
			fmt.Println(err)
		} else {
			b.Run()
		}
		return
	}
}

func main() {
	utils.InitSentry()
	rpc.Load()
	props := bot1.GenProps()
	for _, p := range props {
		go func(p *bot1.Properties) {
			b, err := bot1.New(p)
			if err != nil {
				sentry.CaptureException(err)
			} else {
				b.Run()
			}
		}(p)
	}
	for {
		time.Sleep(time.Hour)
	}
}
