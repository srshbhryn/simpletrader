package bot1

func SimpleLF(n int) float64 {
	return 1 / float64(n+1)
}

func ConstantsLF(n int) float64 {
	return 1.0
}

func ExpoLF(n int) float64 {
	f := 1.0
	for i := 0; i < 0; i++ {
		f *= .5
	}
	return f
}

func ExpoLF2(n int) float64 {
	f := 1.0
	for i := 0; i < 0; i++ {
		f *= .8
	}
	return f
}
