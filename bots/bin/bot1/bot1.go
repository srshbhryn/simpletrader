package main

import (
	"bots/lib/bookwatch"
	"bots/lib/config"
	"bots/lib/config/assets"
	"bots/lib/config/exchanges"
	"bots/lib/config/orderstates"
	"bots/lib/config/pairs"
	"bots/lib/rpc"
	"bots/lib/rpc/trade"
	"fmt"
	"time"
)

func main() {
	rpc.Load()
	config.Load()
	bookwatch.Load()
	createAccountAndCheckBalance()
}

func createAccountAndCheckBalance() {
	uid, err := trade.GetDemoAccount(exchanges.Nobitex)
	if err != nil {
		panic(err)
	}

	trade.SetAccountUUID(uid)
	balance, err := trade.GetBalance(assets.USDT)
	if err != nil {
		panic(err)
	}
	fmt.Println(balance)
}

func planeOrder() {
	orderId, err := trade.PlaceOrder(pairs.UsdtRls, 1, 100, false, nil, nil)
	if err != nil {
		panic(err)
	}
	fmt.Println("orderId is", orderId)
	for {
		time.Sleep(2 * time.Second)
		orderState, err := trade.GetOrderStatus(*orderId)
		if err != nil {
			panic(err)
		}

		fmt.Println(orderState.State == orderstates.Open)
		fmt.Println("orderState is", orderState)

	}

}
func printBalances() {

	usdtBalances, err := trade.GetBalance(assets.USDT)
	if err != nil {
		panic(err)
	}
	fmt.Println(usdtBalances)
	rlsBalances, err := trade.GetBalance(assets.RLS)
	if err != nil {
		panic(err)
	}
	fmt.Println(rlsBalances)

}
