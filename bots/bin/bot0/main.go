package main

import (
	"bots/bin/bot0/bot0"
	"bots/lib/config"
	"bots/lib/rpc"
	"bots/lib/utils"
)

func main() {
	rpc.Load()
	config.Load()
	utils.InitSentry()
	err := bot0.Run()
	if err != nil {
		panic(err)
	}
}
