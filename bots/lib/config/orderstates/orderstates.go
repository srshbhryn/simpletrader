package orderstates

func Load() {}

type OrderState int64

const (
	Open     OrderState = 1
	Failed              = 2
	Canceled            = 3
	Filled              = 4
)

var ALL = [4]OrderState{
	Open,
	Failed,
	Canceled,
	Filled,
}
