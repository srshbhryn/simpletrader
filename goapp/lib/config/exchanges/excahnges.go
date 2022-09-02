package exchanges

import (
	"encoding/json"
	"os"
)

func Load() {}

func init() {
	configDir := os.Getenv("CONFIG_DIR")
	configFile := configDir + "exchanges.json"
	load(configFile)
}

type Exchange struct {
	Id   int    `json:"id"`
	Name string `json:"name"`
}

var instanceById map[int]*Exchange
var instanceByName map[string]*Exchange

func ById(id int) *Exchange {
	return instanceById[id]
}
func ByName(name string) *Exchange {
	return instanceByName[name]
}

func load(filePath string) {
	dat, err := os.ReadFile(filePath)
	if err != nil {
		panic(err)
	}
	var instances []Exchange
	err = json.Unmarshal(dat, &instances)
	if err != nil {
		panic(err)
	}
	instanceById = make(map[int]*Exchange)
	instanceByName = make(map[string]*Exchange)
	for _, instance := range instances {
		instanceById[instance.Id] = &instance
		instanceByName[instance.Name] = &instance
	}
}
