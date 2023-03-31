package main

import (
	"bots/bin/bot1/bot1"
	"bots/lib/rpc"
	"bots/lib/utils"
	"fmt"
	"time"
)

func main() {
	utils.InitSentry()
	rpc.Load()
	props := bot1.GenProps()
	for _, p := range props {
		b, err := bot1.New(p)
		if err != nil {
			fmt.Println(err)
		} else {
			b.Run()
		}
	}
	for {
		time.Sleep(time.Hour)
	}
}
