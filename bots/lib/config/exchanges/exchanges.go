package exchanges

func Load() {}

type Exchange int64

const (
	Nobitex Exchange = 1
)

var ALL = [1]Exchange{
	Nobitex,
}
