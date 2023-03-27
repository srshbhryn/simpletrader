package bot1

import "sync"

type Order struct {
	isSell bool
	amount float64
	price  float64
}

var orderPool sync.Pool

func init() {
	orderPool = sync.Pool{
		New: func() interface{} {
			return &Order{}
		},
	}
}
