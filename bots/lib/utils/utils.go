package utils

import (
	"os"
	"time"

	"github.com/getsentry/sentry-go"
)

func InitSentry() error {
	env := os.Getenv("ENV")
	if env == "" {
		env = "DEBUG"
	}
	err := sentry.Init(sentry.ClientOptions{
		Dsn:              "https://5d806674bd974b2c96828c15918ad0c8@sentry.itshouldbe.fun/4",
		Environment:      env,
		TracesSampleRate: 1.0,
		Debug:            env != "PROD",
	})
	if err == nil {
		go func() {
			for {
				time.Sleep(2 * time.Second)
				sentry.Flush(time.Minute)
			}
		}()

	}
	return err
}
