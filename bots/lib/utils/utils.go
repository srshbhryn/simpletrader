package utils

import (
	"os"

	"github.com/getsentry/sentry-go"
)

func InitSentry() error {
	env := os.Getenv("ENV")
	if env == "" {
		env = "PROD"
	}
	return sentry.Init(sentry.ClientOptions{
		Dsn:              "https://29b2bc84969842cea5cf75790930a22f@sentry.itshouldbe.fun/5",
		Environment:      env,
		TracesSampleRate: 1.0,
	})
}
