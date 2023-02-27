package bot0

type State int

const (
	initial State = iota
	waitToEnter
	waitToExit
)
