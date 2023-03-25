package trader

import "bots/lib/config/exchanges"

type Trader struct {
	accountUUID string
	exchange    exchanges.Exchange
}

func New(exchange exchanges.Exchange) (*Trader, error) {
	accountId, err := getDemoAccount(exchanges.Nobitex)
	if err != nil {
		return nil, err
	}
	return &Trader{accountId, exchange}, nil
}
