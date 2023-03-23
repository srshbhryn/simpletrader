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
		Dsn:              "https://29b2bc84969842cea5cf75790930a22f@sentry.itshouldbe.fun/5",
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
