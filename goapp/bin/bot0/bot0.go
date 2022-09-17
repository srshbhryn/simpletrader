package main

import (
	"fmt"
	"goapp/lib/trader"
	"time"
)

func init() {
	trader.Load()
}

func main() {
	args := "{\"x\":3,\"y\":5}"
	// for {
	response, err := trader.Call("trader.place_order", args)
	if err != nil {
		fmt.Println("error")
		fmt.Println(err)
	}
	fmt.Println(response)
	time.Sleep(10 * time.Second)
	// }/
}
