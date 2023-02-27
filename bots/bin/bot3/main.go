package main

import (
	"fmt"
	"log"
	"time"

	"github.com/getsentry/sentry-go"
)

func main() {
	err := sentry.Init(sentry.ClientOptions{
		Dsn: "https://d97f9f3d4dbe4296804c12e1bca1eaa8@sentry.itshouldbe.fun/3",
		// Set TracesSampleRate to 1.0 to capture 100%
		// of transactions for performance monitoring.
		// We recommend adjusting this value in production,
		TracesSampleRate: 1.0,
	})
	if err != nil {
		log.Fatalf("sentry.Init: %s", err)
	}
	defer func() {
		if r := recover(); r != nil {
			sentry.CaptureMessage("AAAA")
		}
		sentry.Flush(2 * time.Second)
	}()
	// Flush buffered events before the program terminates.
	a := 1
	b := 0
	fmt.Println(a / b)
}
